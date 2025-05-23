# YakuzaPS3-AuthParser

A Python-based tool for **extracting** and **injecting** text from `Auth.bin` files used in PS3 releases of the *Yakuza* series. Built for fan-translation workflows, this script exports editable JSON with hex offsets and reinserts translations while preserving structure and pointer integrity.

## Features

* **Header validation**
  Verifies that the file begins with the `AUTH` signature (ASCII: `41 55 54 48`).

* **Pointer resolution**
  Reads a 2-byte big-endian pointer at offset `0xAA` to locate the start of the string table.

* **String parsing**

  1. Reads the string count (2 bytes, big-endian) located 34 bytes after the pointer offset.
  2. Iterates over null-terminated strings starting from the calculated string data offset.
  3. Decodes each string as Latin-1, replaces `0xB7` with em dash (`—`), and filters out raw entries ≤2 bytes.

* **JSON export**
  Outputs a file named `FILENAME_translated.json` containing an array of objects with hex offsets:

  ```json
  [
    {
      "offset": "0x1F80",
      "string": "This Kazuma Kiryu?"
    },
    {
      "offset": "0x2090",
      "string": "Ex-Chairman of the Tojo?"
    }
  ]
  ```

* **Injection**

  1. Reads and parses the JSON, converting each `offset` to an integer.
  2. Encodes and inserts the new string in place, maintaining padding and block boundaries.
  3. Reapplies 4-byte duration values preceding each string.
  4. Writes the result to `FILENAME_injected.bin`.

## Usage

```bash
# Extract strings to JSON
python YakuzaPS3_AuthParser.py extract path/to/Auth.bin
# → generates path/to/Auth_translated.json

# Edit the JSON: update each "string" value to your translation

# Inject translations into a new binary
python YakuzaPS3_AuthParser.py inject path/to/Auth.bin path/to/Auth_translated.json
# → generates path/to/Auth_injected.bin
```

## Notes

* All `offset` values in the JSON are hexadecimal.
* The script checks available space and adjusts padding automatically.
* Make backups of your original `Auth.bin` file before injecting.
* Always test injected files in-game to ensure correctness.

## Disclaimer

* This tool **only** replaces string content and preserves internal file consistency.
* Use at your own risk. Validate the output in context (e.g., in-game behavior).
