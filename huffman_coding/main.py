import heapq
from collections import Counter
from typing import Iterable


class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(text):
    freq = Counter(text)
    heap = [Node(char, f) for char, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return
    if node.char is not None:
        codes[node.char] = prefix or "0"
    build_codes(node.left, prefix + "0", codes)
    build_codes(node.right, prefix + "1", codes)
    return codes


def huffman_encode(text):
    root = build_tree(text)
    codes = build_codes(root, "", {})
    encoded = "".join(codes[c] for c in text)
    return encoded, codes, root


def huffman_decode(encoded, root):
    result, node = [], root
    for bit in encoded:
        node = node.left if bit == "0" else node.right
        if node.char is not None:
            result.append(node.char)
            node = root
    return "".join(result)


def compact_rows(items: Iterable[str], columns=3, cell_width=24):
    line_cells = []
    for index, item in enumerate(items, start=1):
        text = item
        if len(text) > cell_width - 1:
            text = text[: cell_width - 2] + "."
        line_cells.append(f"{text:<{cell_width}}")
        if index % columns == 0:
            yield "".join(line_cells).rstrip()
            line_cells = []
    if line_cells:
        yield "".join(line_cells).rstrip()


def chunk_text(text: str, width=64):
    for start in range(0, len(text), width):
        yield text[start : start + width]


text = "huffman coding is a lossless data compression algorithm"

freq = Counter(text)
encoded, codes, root = huffman_encode(text)
decoded = huffman_decode(encoded, root)
original_bits = len(text) * 8
ratio = (1 - len(encoded) / original_bits) * 100

print("Original text :", text)
print(
    f"Sizes -> chars: {len(text)} | original: {original_bits} bits | "
    f"encoded: {len(encoded)} bits | saved: {ratio:.1f}%"
)
preview = encoded[:128]
print("Encoded preview:")
for line in chunk_text(preview, width=64):
    print(f"  {line}")
if len(encoded) > len(preview):
    print("  ...")

print("Character frequencies:")
frequency_items = [
    f"{repr(char)}:{count}" for char, count in sorted(freq.items(), key=lambda x: -x[1])
]
for row in compact_rows(frequency_items, columns=4, cell_width=18):
    print(f"  {row}")

print("Huffman codes:")
code_items = [
    f"{repr(char)}:{code}"
    for char, code in sorted(codes.items(), key=lambda x: len(x[1]))
]
for row in compact_rows(code_items, columns=3, cell_width=24):
    print(f"  {row}")

print(f"Decoded text: {decoded}")
print(f"Lossless check: {'PASS' if decoded == text else 'FAIL'}")
