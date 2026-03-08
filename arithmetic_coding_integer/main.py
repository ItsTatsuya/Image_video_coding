import argparse
import json
from collections import Counter

EOF_SYMBOL = "__EOF__"
STATE_BITS = 32
FULL_RANGE = 1 << STATE_BITS
HALF_RANGE = FULL_RANGE >> 1
QUARTER_RANGE = HALF_RANGE >> 1
THREE_QUARTER_RANGE = QUARTER_RANGE * 3


class FrequencyTable:
    def __init__(self, frequencies: dict[str, int]):
        if not frequencies:
            raise ValueError("Frequency table must not be empty.")
        if EOF_SYMBOL not in frequencies:
            raise ValueError(f"Frequency table must include {EOF_SYMBOL}.")
        if any(count <= 0 for count in frequencies.values()):
            raise ValueError("All frequencies must be positive integers.")

        self.symbols = list(frequencies.keys())
        self.frequencies = dict(frequencies)
        self.cumulative: dict[str, tuple[int, int]] = {}

        total = 0
        for symbol in self.symbols:
            low = total
            total += self.frequencies[symbol]
            self.cumulative[symbol] = (low, total)
        self.total = total

    def low(self, symbol: str) -> int:
        return self.cumulative[symbol][0]

    def high(self, symbol: str) -> int:
        return self.cumulative[symbol][1]

    def symbol_for_value(self, value: int) -> str:
        for symbol in self.symbols:
            low, high = self.cumulative[symbol]
            if low <= value < high:
                return symbol
        raise ValueError("Value is outside the frequency table range.")


class ArithmeticEncoder:
    def __init__(self, frequencies: FrequencyTable):
        self.frequencies = frequencies
        self.low = 0
        self.high = FULL_RANGE - 1
        self.pending_bits = 0
        self.output_bits: list[str] = []

    def encode_symbol(self, symbol: str) -> None:
        total = self.frequencies.total
        symbol_low = self.frequencies.low(symbol)
        symbol_high = self.frequencies.high(symbol)
        current_range = self.high - self.low + 1

        self.high = self.low + (current_range * symbol_high // total) - 1
        self.low = self.low + (current_range * symbol_low // total)

        while True:
            if self.high < HALF_RANGE:
                self.write_bit(0)
            elif self.low >= HALF_RANGE:
                self.write_bit(1)
                self.low -= HALF_RANGE
                self.high -= HALF_RANGE
            elif self.low >= QUARTER_RANGE and self.high < THREE_QUARTER_RANGE:
                self.pending_bits += 1
                self.low -= QUARTER_RANGE
                self.high -= QUARTER_RANGE
            else:
                break

            self.low = self.low << 1
            self.high = (self.high << 1) | 1

    def write_bit(self, bit: int) -> None:
        self.output_bits.append(str(bit))
        opposite = "1" if bit == 0 else "0"
        for _ in range(self.pending_bits):
            self.output_bits.append(opposite)
        self.pending_bits = 0

    def finish(self) -> str:
        self.pending_bits += 1
        if self.low < QUARTER_RANGE:
            self.write_bit(0)
        else:
            self.write_bit(1)
        return "".join(self.output_bits)


class ArithmeticDecoder:
    def __init__(self, bits: str, frequencies: FrequencyTable):
        if any(bit not in "01" for bit in bits):
            raise ValueError("Encoded arithmetic bitstream must contain only 0 and 1.")

        self.bits = bits
        self.index = 0
        self.frequencies = frequencies
        self.low = 0
        self.high = FULL_RANGE - 1
        self.code = 0

        for _ in range(STATE_BITS):
            self.code = (self.code << 1) | self.read_bit()

    def read_bit(self) -> int:
        if self.index >= len(self.bits):
            return 0
        bit = 1 if self.bits[self.index] == "1" else 0
        self.index += 1
        return bit

    def decode_symbol(self) -> str:
        total = self.frequencies.total
        current_range = self.high - self.low + 1
        value = ((self.code - self.low + 1) * total - 1) // current_range
        symbol = self.frequencies.symbol_for_value(value)

        symbol_low = self.frequencies.low(symbol)
        symbol_high = self.frequencies.high(symbol)
        self.high = self.low + (current_range * symbol_high // total) - 1
        self.low = self.low + (current_range * symbol_low // total)

        while True:
            if self.high < HALF_RANGE:
                pass
            elif self.low >= HALF_RANGE:
                self.low -= HALF_RANGE
                self.high -= HALF_RANGE
                self.code -= HALF_RANGE
            elif self.low >= QUARTER_RANGE and self.high < THREE_QUARTER_RANGE:
                self.low -= QUARTER_RANGE
                self.high -= QUARTER_RANGE
                self.code -= QUARTER_RANGE
            else:
                break

            self.low = self.low << 1
            self.high = (self.high << 1) | 1
            self.code = (self.code << 1) | self.read_bit()

        return symbol


def build_frequency_dict(message: str) -> dict[str, int]:
    counts = Counter(message)
    ordered_symbols = sorted(counts)
    frequencies = {symbol: counts[symbol] for symbol in ordered_symbols}
    frequencies[EOF_SYMBOL] = 1
    return frequencies


def encode_message(
    message: str, frequencies: dict[str, int] | None = None
) -> tuple[str, dict[str, int]]:
    if frequencies is None:
        frequencies = build_frequency_dict(message)
    table = FrequencyTable(frequencies)
    encoder = ArithmeticEncoder(table)
    for symbol in message:
        if symbol not in table.frequencies:
            raise ValueError(f"Symbol {symbol!r} is missing from the frequency table.")
        encoder.encode_symbol(symbol)
    encoder.encode_symbol(EOF_SYMBOL)
    return encoder.finish(), table.frequencies


def decode_message(bits: str, frequencies: dict[str, int]) -> str:
    table = FrequencyTable(frequencies)
    decoder = ArithmeticDecoder(bits, table)
    output: list[str] = []

    while True:
        symbol = decoder.decode_symbol()
        if symbol == EOF_SYMBOL:
            return "".join(output)
        output.append(symbol)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Integer arithmetic coding with a static model."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode a message.")
    encode_parser.add_argument("--message", required=True, help="Message to encode.")
    encode_parser.add_argument("--model", help="JSON dictionary of frequencies.")

    decode_parser = subparsers.add_parser("decode", help="Decode a message.")
    decode_parser.add_argument(
        "--bits", required=True, help="Arithmetic coded bitstream."
    )
    decode_parser.add_argument(
        "--model", required=True, help="JSON dictionary of frequencies."
    )

    demo_parser = subparsers.add_parser(
        "demo", help="Encode and immediately decode a message."
    )
    demo_parser.add_argument("--message", required=True, help="Message to process.")

    return parser


def parse_model(raw_model: str | None) -> dict[str, int] | None:
    if raw_model is None:
        return None
    model = json.loads(raw_model)
    if not isinstance(model, dict):
        raise ValueError("Model must be a JSON object mapping symbols to frequencies.")
    parsed: dict[str, int] = {}
    for key, value in model.items():
        if not isinstance(key, str) or not isinstance(value, int):
            raise ValueError("Model keys must be strings and values must be integers.")
        parsed[key] = value
    return parsed


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "encode":
            model = parse_model(args.model)
            bits, frequencies = encode_message(args.message, model)
            print(f"Message: {args.message}")
            print(f"Encoded bitstream: {bits}")
            print(f"Model: {json.dumps(frequencies, ensure_ascii=True)}")
        elif args.command == "decode":
            model = parse_model(args.model)
            if model is None:
                raise ValueError("A model is required for decoding.")
            message = decode_message(args.bits, model)
            print(f"Decoded message: {message}")
        else:
            bits, frequencies = encode_message(args.message)
            message = decode_message(bits, frequencies)
            print(f"Original message: {args.message}")
            print(f"Encoded bitstream: {bits}")
            print(f"Model: {json.dumps(frequencies, ensure_ascii=True)}")
            print(f"Decoded message: {message}")
    except (ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
