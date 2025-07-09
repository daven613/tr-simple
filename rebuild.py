#!/usr/bin/env python3
"""
rebuild.py - Rebuild processed chunks into final output file
"""

import json
import argparse
import os
from pathlib import Path


def rebuild_chunks(json_file, output_file=None):
    """Rebuild processed chunks into a final text file."""
    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If no output file specified, create default name
    if not output_file:
        base_name = Path(json_file).stem.replace('_chunked', '')
        output_file = f"{base_name}_final.txt"
    
    # Collect statistics
    total_chunks = len(data['chunks'])
    done_chunks = []
    error_chunks = []
    pending_chunks = []
    
    for chunk in data['chunks']:
        if chunk['status'] == 'done':
            done_chunks.append(chunk)
        elif chunk['status'] == 'error':
            error_chunks.append(chunk['index'])
        else:
            pending_chunks.append(chunk['index'])
    
    print(f"📊 Chunk Statistics:")
    print(f"- Total chunks: {total_chunks}")
    print(f"- Completed: {len(done_chunks)}")
    print(f"- Errors: {len(error_chunks)}")
    print(f"- Pending: {len(pending_chunks)}")
    
    if error_chunks:
        print(f"\n⚠️  Warning: Found {len(error_chunks)} chunks with errors: {error_chunks}")
    
    if pending_chunks:
        print(f"\n⚠️  Warning: Found {len(pending_chunks)} pending chunks: {pending_chunks}")
    
    if not done_chunks:
        print("\n❌ No completed chunks found. Nothing to rebuild.")
        return 1
    
    # Sort chunks by index to maintain order
    done_chunks.sort(key=lambda x: x['index'])
    
    # Rebuild text from results
    rebuilt_text = ""
    for chunk in done_chunks:
        if chunk['result']:
            rebuilt_text += chunk['result']
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rebuilt_text)
    
    # Calculate file size
    file_size = os.path.getsize(output_file)
    size_kb = file_size / 1024
    
    print(f"\n✅ Successfully rebuilt {len(done_chunks)} chunks")
    print(f"📄 Output file: {output_file}")
    print(f"📏 File size: {size_kb:.1f} KB ({file_size:,} bytes)")
    
    if error_chunks or pending_chunks:
        incomplete_count = len(error_chunks) + len(pending_chunks)
        print(f"\n⚠️  Note: Output is incomplete. Missing {incomplete_count} chunks.")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description='Rebuild processed chunks into final file')
    parser.add_argument('json_file', help='Processed JSON file to rebuild')
    parser.add_argument('-o', '--output', help='Output file name (optional)')
    
    args = parser.parse_args()
    
    # Validate JSON file exists
    if not os.path.exists(args.json_file):
        print(f"❌ Error: JSON file '{args.json_file}' not found")
        return 1
    
    # Rebuild chunks
    return rebuild_chunks(args.json_file, args.output)


if __name__ == "__main__":
    exit(main())