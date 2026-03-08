# Image Video Coding Algorithms

This workspace contains three standalone Python implementations:

1. `unique_decodable` checks whether a set of binary codewords is uniquely decodable and whether it is a prefix code.
2. `coloumb_code` implements Golomb coding for non-negative integers.
3. `arithmetic_coding_integer` implements integer arithmetic coding with a static frequency model.

## Requirements

- Python 3.10 or newer

## Project Structure

```text
Image_video_coding/
├── arithmetic_coding_integer/
│   └── main.py
├── coloumb_code/
│   └── main.py
├── unique_decodable/
│   └── main.py
└── README.md
```

## 1. Unique Decodability And Prefix Check

This module uses the Sardinas-Patterson algorithm to test unique decodability.

Run:

```bash
python unique_decodable/main.py 0 01 11
```

Example output:

```text
Codewords: ['0', '01', '11']
Prefix code: False
Uniquely decodable: True
```

## 2. Coloumb Code

The folder name follows your request. The implementation inside is Golomb coding, which is the standard source-coding method usually intended by this name.

Encode numbers with parameter `m`:

```bash
python coloumb_code/main.py encode --m 5 --values 3 7 10
```

Decode a concatenated bitstream:

```bash
python coloumb_code/main.py decode --m 5 --bits 1011001001 --count 3
```

## 3. Integer Arithmetic Coding

This module implements static-model arithmetic coding using integer range updates and bit renormalization.

Encode a message and automatically build the model from the message:

```bash
python arithmetic_coding_integer/main.py encode --message BANANA
```

Decode a bitstream with a supplied model:

```bash
python arithmetic_coding_integer/main.py decode --bits 010101 --model "{\"A\": 3, \"B\": 1, \"N\": 2, \"__EOF__\": 1}"
```

Run a full encode-decode cycle:

```bash
python arithmetic_coding_integer/main.py demo --message BANANA
```

## Notes

- The unique decodability checker expects binary strings only.
- The Golomb coder works on non-negative integers.
- The arithmetic coder uses a reserved end-of-stream symbol named `__EOF__`.

## Tests

Run the full test suite from the workspace root:

```bash
python -m unittest discover -s tests -v
```
