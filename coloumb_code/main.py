import argparse
import math


def validate_non_negative(values: list[int]) -> None:
    if any(value < 0 for value in values):
        raise ValueError("Golomb coding requires non-negative integers.")


def validate_parameter(m: int) -> None:
    if m <= 0:
        raise ValueError("Parameter m must be a positive integer.")


def encode_unary(value: int) -> str:
    return "1" * value + "0"


def decode_unary(bits: str, index: int) -> tuple[int, int]:
    quotient = 0
    while index < len(bits) and bits[index] == "1":
        quotient += 1
        index += 1
    if index >= len(bits) or bits[index] != "0":
        raise ValueError("Invalid unary prefix in bitstream.")
    return quotient, index + 1


def encode_remainder(remainder: int, m: int) -> str:
    if m == 1:
        return ""
    bits = math.ceil(math.log2(m))
    cutoff = (1 << bits) - m
    if remainder < cutoff:
        return format(remainder, f"0{bits - 1}b")
    return format(remainder + cutoff, f"0{bits}b")


def decode_remainder(bits: str, index: int, m: int) -> tuple[int, int]:
    if m == 1:
        return 0, index
    width = math.ceil(math.log2(m))
    cutoff = (1 << width) - m

    short_width = width - 1
    if index + short_width > len(bits):
        raise ValueError("Bitstream ended while decoding Golomb remainder.")

    probe = int(bits[index : index + short_width], 2) if short_width else 0
    if probe < cutoff:
        return probe, index + short_width

    if index + width > len(bits):
        raise ValueError("Bitstream ended while decoding Golomb remainder.")
    value = int(bits[index : index + width], 2)
    return value - cutoff, index + width


def encode_number(value: int, m: int) -> str:
    validate_parameter(m)
    validate_non_negative([value])
    quotient, remainder = divmod(value, m)
    return encode_unary(quotient) + encode_remainder(remainder, m)


def decode_number(bits: str, m: int, index: int = 0) -> tuple[int, int]:
    validate_parameter(m)
    quotient, index = decode_unary(bits, index)
    remainder, index = decode_remainder(bits, index, m)
    return quotient * m + remainder, index


def encode_sequence(values: list[int], m: int) -> str:
    validate_non_negative(values)
    return "".join(encode_number(value, m) for value in values)


def decode_stream(bits: str, m: int, count: int | None = None) -> list[int]:
    values: list[int] = []
    index = 0
    while index < len(bits) and (count is None or len(values) < count):
        value, index = decode_number(bits, m, index)
        values.append(value)

    if count is not None and len(values) != count:
        raise ValueError(
            "Bitstream ended before the requested number of values was decoded."
        )
    if count is None and index != len(bits):
        raise ValueError("Bitstream contains an incomplete Golomb codeword.")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Encode and decode Golomb codes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode integers.")
    encode_parser.add_argument("--m", type=int, required=True, help="Golomb parameter.")
    encode_parser.add_argument(
        "--values", type=int, nargs="+", required=True, help="Values to encode."
    )

    decode_parser = subparsers.add_parser("decode", help="Decode a bitstream.")
    decode_parser.add_argument("--m", type=int, required=True, help="Golomb parameter.")
    decode_parser.add_argument(
        "--bits", required=True, help="Concatenated Golomb bitstream."
    )
    decode_parser.add_argument("--count", type=int, help="Number of values to decode.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "encode":
            bitstream = encode_sequence(args.values, args.m)
            print(f"Values: {args.values}")
            print(f"m: {args.m}")
            print(f"Encoded bitstream: {bitstream}")
        else:
            values = decode_stream(args.bits, args.m, args.count)
            print(f"Bitstream: {args.bits}")
            print(f"m: {args.m}")
            print(f"Decoded values: {values}")
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
