import argparse
import struct
import os
import re
import json

def read_be_uint16(data, offset):
    return struct.unpack_from('>H', data, offset)[0]

def extract_strings(bin_path, output_json):
    with open(bin_path, 'rb') as f:
        data = f.read()

    if data[:4] != b'AUTH':
        raise ValueError('Invalid header, expected AUTH at start')

    ptr_table    = read_be_uint16(data, 0xAA)
    count_offset = ptr_table + 34
    num_strings  = read_be_uint16(data, count_offset)
    first_str    = count_offset + 2 + 28

    entries = []
    pos = first_str
    while len(entries) < num_strings and pos < len(data):
        end = data.find(b'\x00', pos)
        if end < 0:
            break
        raw = data[pos:end]
        if len(raw) > 2:
            s = raw.decode('latin-1').replace('\u00B7', '—')
            entries.append({
                "offset": f"0x{pos:X}",
                "text":   s
            })
        pos = end + 1

    with open(output_json, 'w', encoding='utf-8') as jf:
        json.dump(entries, jf, ensure_ascii=False, indent=2)

    print(f'Extracted {len(entries)} strings to {output_json}')


def inject_strings(bin_path, json_path, output_bin):
    data = bytearray(open(bin_path, 'rb').read())
    with open(json_path, 'r', encoding='utf-8') as jf:
        raw_entries = json.load(jf)
    entries = []
    for e in raw_entries:
        off = int(e["offset"], 16)
        entries.append((off, e["text"]))
    entries.sort(key=lambda x: x[0])
    durations = {
        off: data[off-4:off] if off>=4 else b''
        for off, _ in entries
    }
    for idx, (off, text) in enumerate(entries):
        orig_end = data.find(b'\x00', off)
        if orig_end < 0:
            continue

        if idx + 1 < len(entries):
            next_off  = entries[idx+1][0]
            dur_limit = next_off - 4
        else:
            dur_limit = len(data)

        avail_end = orig_end
        while avail_end + 1 < dur_limit and data[avail_end+1] == 0x00:
            avail_end += 1

        available_space = avail_end - off + 1

        buf = bytearray()
        for ch in text:
            if ch == '—':
                buf.append(0xB7)
            else:
                buf.extend(ch.encode('utf-8'))
        encoded = bytes(buf) + b'\x00'

        if len(encoded) > available_space:
            raise ValueError(
                f"Translated string at 0x{off:X} "
                f"({len(encoded)} bytes) exceeds available {available_space} bytes"
            )

        data[off:off+available_space] = (
            encoded + b'\x00' * (available_space - len(encoded))
        )

    for off, dbytes in durations.items():
        if dbytes:
            data[off-4:off] = dbytes
    with open(output_bin, 'wb') as out:
        out.write(data)

    print(f'Injected translations into {output_bin}')


def main():
    p = argparse.ArgumentParser(
        prog='YakuzaPS3_AuthParser',
        description='Extract/inject AUTH.bin strings as JSON with hex offsets'
    )
    p.add_argument('mode', choices=['extract','inject'], help='Mode')
    p.add_argument('binfile', help='Path to .bin file')
    p.add_argument('jsonfile', nargs='?', help='JSON file for inject or output for extract')
    args = p.parse_args()

    if args.mode == 'extract':
        out_json = args.jsonfile or os.path.splitext(args.binfile)[0] + '_strings.json'
        extract_strings(args.binfile, out_json)
    else:
        if not args.jsonfile:
            p.error('inject mode requires a JSON file')
        inject_strings(
            args.binfile,
            args.jsonfile,
            os.path.splitext(args.binfile)[0] + '_injected.bin'
        )

if __name__ == '__main__':
    main()
