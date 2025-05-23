# YakuzaPS3-AuthParser

A Python-based tool for extracting and re‑injecting text from/to **Auth.bin** files used in PS3 releases of the *Yakuza* series. This utility is designed to assist fan‑translation workflows by automating string extraction, JSON export, and reinsertion with automatic padding and pointer updates.

## Features

* **Header validation**: Ensures the file starts with `AUTH` signature (bytes `41 55 54 48`).
* **Pointer resolution**: Reads a big‑endian 2‑byte pointer at offset `0xAA`, navigates to the text payload.
* **String parsing**:

  * Reads the count of strings (2 bytes BE after 34 bytes offset).
  * Locates each string (null‑terminated), extracts it, and computes block padding (16-byte alignment + 240-byte skip + 16-byte data block).
* **JSON export**: Outputs `FILENAME_translated.json` containing an array of objects:

  ```json
  [
    { "offset": "0x012A",
      "string": "Original text here" }
  ]
  ```
* **Injection**:

  * Reads the JSON, sorts by offset, and splices in translated strings.
  * Recalculates block padding (expanding or shrinking as needed).
  * Tracks filesize changes and updates two headers:

    * 2‑byte BE pointer at offset `0x12` → start of final 16‑byte block.
    * 2‑byte BE value at offset `0x3A` → last byte index of the file.

## Requirements

* Python 3.6+
* No external dependencies (uses only Python stdlib)

## Usage

```bash
# Extract strings to JSON
python YakuzaPS3_AuthParser.py extract path/to/Auth.bin
# → generates path/to/Auth_translated.json

# Edit the JSON: change each "string" value to your translation.

# Inject translations back into a new .bin
python YakuzaPS3_AuthParser.py inject path/to/Auth.bin path/to/Auth_translated.json
# → generates path/to/Auth_injected.bin
```

## Notes

* Offsets in the JSON are in hexadecimal for clarity.
* You can exceed the original text length; the script will adjust padding and file size accordingly.
* Always backup your original `Auth.bin` before injecting.
* Test the injected file in‑game to confirm correctness.

## Disclaimer

* This tool **only** replaces text, adjusts padding, and updates two header pointers.
* Use at your own risk and verify output manually in the game.
