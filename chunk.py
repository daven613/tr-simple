#!/usr/bin/env python3
"""
chunk.py - Split large text files into manageable chunks for processing
"""

import json
import argparse
import os
from pathlib import Path


def chunk_text(text, chunk_size):
    """Split text into chunks respecting boundaries: newline > period > comma > space > mid-word."""
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate the ideal end position
        end = start + chunk_size
        
        # If we're at the end of the text, take everything
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Look for the best breaking point, searching backwards from the ideal position
        # Priority order: newline > period > comma > space > mid-word
        best_break = end  # Default to mid-word if nothing else found
        
        # Search within a reasonable window (50% of chunk size)
        search_start = max(start, end - int(chunk_size * 0.5))
        
        # First, look for newline
        newline_pos = text.rfind('\n', search_start, end)
        if newline_pos != -1:
            best_break = newline_pos + 1
        else:
            # Look for period
            period_pos = text.rfind('.', search_start, end)
            if period_pos != -1:
                best_break = period_pos + 1
            else:
                # Look for comma
                comma_pos = text.rfind(',', search_start, end)
                if comma_pos != -1:
                    best_break = comma_pos + 1
                else:
                    # Look for space
                    space_pos = text.rfind(' ', search_start, end)
                    if space_pos != -1:
                        best_break = space_pos + 1
                    # Otherwise, keep the mid-word break (best_break = end)
        
        # Extract the chunk
        chunks.append(text[start:best_break])
        start = best_break
    
    return chunks


def create_chunked_file(input_file, chunk_size):
    """Create a chunked JSON file from input text file."""
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create chunks
    chunks = chunk_text(text, chunk_size)
    
    # Create output filename
    base_name = Path(input_file).stem
    output_file = f"{base_name}_chunked.json"
    
    # Create JSON structure
    data = {
        "meta": {
            "book_id": base_name,
            "chunk_size": chunk_size,
            "total_chunks": len(chunks)
        },
        "chunks": []
    }
    
    # Add chunks to data structure
    for i, chunk in enumerate(chunks):
        data["chunks"].append({
            "index": i,
            "text": chunk,
            "status": "pending",
            "result": None
        })
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {output_file}")
    print(f"📊 Total chunks: {len(chunks)}")
    print(f"📏 Chunk size: {chunk_size} characters")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description='Chunk a text file into manageable pieces')
    parser.add_argument('input_file', help='Input text file to chunk')
    parser.add_argument('--chunk-size', type=int, default=2000, 
                       help='Size of each chunk in characters (default: 2000)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    # Create chunked file
    create_chunked_file(args.input_file, args.chunk_size)
    return 0


if __name__ == "__main__":
    exit(main())