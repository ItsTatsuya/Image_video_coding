import argparse
from typing import Iterable


def validate_binary_codewords(codewords: list[str]) -> None:
    if not codewords:
        raise ValueError("At least one codeword is required.")
    if len(set(codewords)) != len(codewords):
        raise ValueError("Codewords must be distinct.")
    invalid = [
        word for word in codewords if not word or any(bit not in "01" for bit in word)
    ]
    if invalid:
        raise ValueError("All codewords must be non-empty binary strings.")


def is_prefix_code(codewords: list[str]) -> bool:
    ordered = sorted(codewords, key=len)
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            if right.startswith(left):
                return False
    return True


def initial_suffixes(codewords: list[str]) -> set[str]:
    suffixes: set[str] = set()
    for left in codewords:
        for right in codewords:
            if left == right:
                continue
            if right.startswith(left):
                suffix = right[len(left) :]
                if suffix:
                    suffixes.add(suffix)
    return suffixes


def next_suffixes(codewords: list[str], current: Iterable[str]) -> set[str]:
    suffixes: set[str] = set()
    for dangling in current:
        for codeword in codewords:
            if dangling.startswith(codeword):
                suffix = dangling[len(codeword) :]
                if suffix:
                    suffixes.add(suffix)
            if codeword.startswith(dangling):
                suffix = codeword[len(dangling) :]
                if suffix:
                    suffixes.add(suffix)
    return suffixes


def sardinas_patterson(codewords: list[str]) -> tuple[bool, list[list[str]]]:
    codeword_set = set(codewords)
    stages: list[list[str]] = []
    seen: set[str] = set()
    current = initial_suffixes(codewords)

    while current:
        ordered = sorted(current)
        stages.append(ordered)
        if current & codeword_set:
            return False, stages

        fresh = current - seen
        if not fresh:
            return True, stages

        seen.update(current)
        current = next_suffixes(codewords, fresh) - seen

    return True, stages


def analyze(codewords: list[str]) -> tuple[bool, bool, list[list[str]]]:
    validate_binary_codewords(codewords)
    prefix = is_prefix_code(codewords)
    uniquely_decodable, stages = sardinas_patterson(codewords)
    return prefix, uniquely_decodable, stages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check prefix property and unique decodability."
    )
    parser.add_argument("codewords", nargs="+", help="Binary codewords to analyze.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        prefix, uniquely_decodable, _ = analyze(args.codewords)
    except ValueError as error:
        parser.error(str(error))
        return

    print(f"Codewords: {args.codewords}")
    print(f"Prefix code: {prefix}")
    print(f"Uniquely decodable: {uniquely_decodable}")


if __name__ == "__main__":
    main()
