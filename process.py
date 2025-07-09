#!/usr/bin/env python3
"""
process.py - Process chunks using LLM with detailed progress tracking
"""

import json
import argparse
import os
import time
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProgressTracker:
    def __init__(self, total_chunks):
        self.total_chunks = total_chunks
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.start_time = time.time()
        self.failed_chunks = []
    
    def update(self, success=True, chunk_index=None):
        self.processed += 1
        if success:
            self.success += 1
        else:
            self.failed += 1
            if chunk_index is not None:
                self.failed_chunks.append(chunk_index)
    
    def get_speed(self):
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return (self.processed / elapsed) * 60  # chunks per minute
        return 0
    
    def get_eta(self, remaining):
        speed = self.get_speed()
        if speed > 0:
            eta_seconds = (remaining / speed) * 60
            return str(timedelta(seconds=int(eta_seconds)))
        return "calculating..."
    
    def get_progress_bar(self, current, total):
        bar_length = 20
        filled = int((current / total) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        speed = self.get_speed()
        eta = self.get_eta(total - current)
        
        return (f"Processing: [{bar}] {current}/{total} chunks | "
                f"✓ {self.success} | ✗ {self.failed} | "
                f"Speed: {speed:.1f}/min | ETA: {eta}")
    
    def get_summary(self):
        elapsed = time.time() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        summary = f"\nSummary:\n"
        summary += f"- Total chunks: {self.total_chunks}\n"
        summary += f"- Successfully processed: {self.success}\n"
        summary += f"- Failed: {self.failed}"
        if self.failed_chunks:
            summary += f" (chunks: {', '.join(map(str, self.failed_chunks))})"
        summary += f"\n- Processing time: {elapsed_str}"
        
        return summary


def process_chunk(client, chunk_text, prompt_template, model):
    """Process a single chunk using the LLM."""
    try:
        # Replace {text} placeholder in prompt
        prompt = prompt_template.replace("{text}", chunk_text)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def process_chunks(json_file, prompt_template, model):
    """Process all pending chunks in the JSON file."""
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        print("❌ Error: OPENAI_KEY not found in .env file")
        return 1
    
    client = OpenAI(api_key=api_key)
    
    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count chunks by status
    pending_chunks = []
    done_count = 0
    
    for i, chunk in enumerate(data['chunks']):
        if chunk['status'] == 'done':
            done_count += 1
        else:
            pending_chunks.append(i)
    
    total_chunks = len(data['chunks'])
    
    print(f"Starting processing of {json_file}")
    print(f"Found {total_chunks} chunks: {len(pending_chunks)} pending, {done_count} already done\n")
    
    if not pending_chunks:
        print("✅ All chunks already processed!")
        return 0
    
    # Initialize progress tracker
    tracker = ProgressTracker(total_chunks)
    tracker.success = done_count  # Account for already done chunks
    
    # Process each pending chunk
    for idx, chunk_index in enumerate(pending_chunks):
        chunk = data['chunks'][chunk_index]
        
        # Show progress
        print(f"\r{tracker.get_progress_bar(idx + 1, len(pending_chunks))}", end='', flush=True)
        
        # Show current chunk preview
        preview = chunk['text'][:50] + "..." if len(chunk['text']) > 50 else chunk['text']
        print(f"\nCurrent: Processing chunk {chunk_index} - \"{preview}\"")
        
        # Process the chunk
        result, error = process_chunk(client, chunk['text'], prompt_template, model)
        
        if result:
            chunk['status'] = 'done'
            chunk['result'] = result
            chunk['error'] = None
            tracker.update(success=True)
        else:
            chunk['status'] = 'error'
            chunk['error'] = error
            tracker.update(success=False, chunk_index=chunk_index)
        
        # Save after each chunk
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Final newline after progress bar
    print()
    
    # Show summary
    print(tracker.get_summary())
    
    return 0


def main():
    parser = argparse.ArgumentParser(description='Process chunks using LLM')
    parser.add_argument('json_file', help='Chunked JSON file to process')
    parser.add_argument('--prompt', required=True, 
                       help='Prompt template (use {text} as placeholder)')
    parser.add_argument('--model', default='gpt-4o-mini-2024-07-18',
                       help='Model to use (default: gpt-4o-mini-2024-07-18)')
    
    args = parser.parse_args()
    
    # Use the model from .env if provided
    env_model = os.getenv('MODEL_NAME')
    if env_model:
        model = env_model
    else:
        model = args.model
    
    # Validate JSON file exists
    if not os.path.exists(args.json_file):
        print(f"❌ Error: JSON file '{args.json_file}' not found")
        return 1
    
    # Process chunks
    return process_chunks(args.json_file, args.prompt, model)


if __name__ == "__main__":
    exit(main())