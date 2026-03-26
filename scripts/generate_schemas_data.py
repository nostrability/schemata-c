#!/usr/bin/env python3
"""Generate schemas_data.h from schemata dist/ directory.

Ports the naming logic from schemata-rs/src/registry.rs.
Produces a sorted C array of {key, json} structs for binary search lookup.
"""

import json
import os
import re
import sys
from pathlib import Path


def sanitize(s: str) -> str:
    """Remove all characters that aren't [a-zA-Z0-9]."""
    return re.sub(r'[^a-zA-Z0-9]', '', s)


def camel_case_hyphens(s: str) -> str:
    """'client-req' -> 'clientReq', 'kind-3' -> 'kind3'."""
    parts = [p for p in s.split('-') if p]
    if not parts:
        return ''
    first = parts[0].lower()
    rest = ''.join(p[0].upper() + p[1:].lower() for p in parts[1:])
    return first + rest


def process_base_name(base_name: str) -> str:
    """If base is 'schema' -> '', if starts with 'schema.' -> capitalize remainder."""
    if base_name == 'schema':
        return ''
    if base_name.startswith('schema.'):
        after = base_name[len('schema.'):]
        if after:
            return after[0].upper() + after[1:]
        return ''
    return base_name


def handle_tag_case(dir_parts: list, base_name: str):
    """Handle tag directory special cases. Returns None if not a tag case."""
    last_dir = dir_parts[-1] if dir_parts else ''
    second_last = dir_parts[-2] if len(dir_parts) >= 2 else ''

    # tag/schema.json -> "tagSchema"
    if last_dir == 'tag' and base_name == 'schema':
        return 'tagSchema'

    # tag/e/schema.json -> "eTagSchema", tag/_A/schema.json -> "ATagSchema"
    if second_last == 'tag':
        if base_name == 'schema':
            name = last_dir
            if name.startswith('_') and len(name) > 1:
                rest = name[1:]
                name = rest[0].upper() + rest[1:]
            return f'{name}TagSchema'
        else:
            return ''  # skip non-schema files in tag subdirs

    # tag/amount.json -> "amountTagSchema", tag/_A.json -> "ATagSchema"
    if last_dir == 'tag' and base_name:
        if base_name.startswith('_') and len(base_name) > 1:
            rest = base_name[1:]
            letter = rest[0].upper() + rest[1:]
            return f'{letter}TagSchema'
        return f'{base_name}TagSchema'

    return None


def generate_nips_export(path: str):
    """Generate export name for nips/ and mips/ files."""
    parts = path.rsplit('/', 1)
    if len(parts) != 2:
        return None
    dir_path, filename = parts
    if not filename.endswith('.json'):
        return None
    base_name = filename[:-5]  # strip .json
    processed = process_base_name(base_name)

    dir_parts = [p for p in dir_path.split('/') if p]

    tag_result = handle_tag_case(dir_parts, base_name)
    if tag_result is not None:
        if not tag_result:
            return None  # skip
        return sanitize(tag_result)

    parent = dir_parts[-1] if dir_parts else ''
    parent_cased = camel_case_hyphens(parent)
    combined = f'{parent_cased}{processed}'
    if not combined:
        combined = 'Unnamed'
    combined += 'Schema'
    return sanitize(combined)


def generate_alias_export(path: str):
    """Generate export name for _aliases/ files."""
    parts = path.rsplit('/', 1)
    if len(parts) != 2:
        return None
    dir_path, filename = parts
    if not filename.endswith('.json'):
        return None
    base_name = filename[:-5]
    processed = process_base_name(base_name)

    dir_parts = [p for p in dir_path.split('/') if p]

    last = dir_parts[-1] if dir_parts else ''
    if last == '@' or last == '_aliases':
        final_name = f'{processed.lower()}Schema'
        return sanitize(final_name)

    tag_result = handle_tag_case(dir_parts, base_name)
    if tag_result is not None:
        if not tag_result:
            return None
        return sanitize(tag_result)

    parent = dir_parts[-1] if dir_parts else ''
    parent_cased = camel_case_hyphens(parent)
    combined = f'{parent_cased}{processed}'
    if not combined:
        combined = 'Unnamed'
    combined += 'Schema'
    return sanitize(combined)


def collect_json_files(base_dir: str, prefix: str):
    """Recursively collect all .json file paths, sorted."""
    results = []
    full_path = os.path.join(base_dir, prefix)
    if not os.path.isdir(full_path):
        return results

    for root, dirs, files in os.walk(full_path):
        dirs.sort()  # deterministic ordering
        for f in sorted(files):
            if f.endswith('.json'):
                rel = os.path.relpath(os.path.join(root, f), base_dir)
                abs_path = os.path.join(root, f)
                results.append((rel, abs_path))
    results.sort(key=lambda x: x[0])
    return results


def escape_c_string(s: str) -> str:
    """Escape a string for C string literal."""
    return (s
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <schemata-dist-dir> <output-header>", file=sys.stderr)
        sys.exit(1)

    dist_dir = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isdir(dist_dir):
        print(f"Error: {dist_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    registry = {}  # export_name -> json_string (first-wins)

    # Process nips/, mips/, _aliases/ in order
    dirs_and_generators = [
        ('nips', generate_nips_export),
        ('mips', generate_nips_export),
        ('@', generate_alias_export),
    ]

    for dir_name, generator in dirs_and_generators:
        entries = collect_json_files(dist_dir, dir_name)
        for rel_path, abs_path in entries:
            export_name = generator(rel_path)
            if export_name and export_name not in registry:
                with open(abs_path, 'r') as f:
                    json_str = f.read().strip()
                    # Verify it's valid JSON
                    try:
                        json.loads(json_str)
                    except json.JSONDecodeError:
                        print(f"Warning: skipping invalid JSON: {rel_path}", file=sys.stderr)
                        continue
                    # Compact the JSON
                    json_str = json.dumps(json.loads(json_str), separators=(',', ':'))
                    registry[export_name] = json_str

    # Sort by key for binary search
    sorted_keys = sorted(registry.keys())

    print(f"Generating {output_file} with {len(sorted_keys)} schemas", file=sys.stderr)

    with open(output_file, 'w') as f:
        f.write("/* Auto-generated by generate_schemas_data.py — DO NOT EDIT */\n")
        f.write("#ifndef SCHEMATA_SCHEMAS_DATA_H\n")
        f.write("#define SCHEMATA_SCHEMAS_DATA_H\n\n")
        f.write("#include <stddef.h>\n\n")

        f.write("typedef struct {\n")
        f.write("    const char *key;\n")
        f.write("    const char *json;\n")
        f.write("} schemata_entry;\n\n")

        f.write(f"#define SCHEMATA_COUNT {len(sorted_keys)}\n\n")

        f.write("static const schemata_entry schemata_entries[SCHEMATA_COUNT] = {\n")
        for key in sorted_keys:
            escaped = escape_c_string(registry[key])
            f.write(f'    {{"{key}", "{escaped}"}},\n')
        f.write("};\n\n")

        f.write("#endif /* SCHEMATA_SCHEMAS_DATA_H */\n")

    # Print key list to stdout for verification
    for key in sorted_keys:
        print(key)


if __name__ == '__main__':
    main()
