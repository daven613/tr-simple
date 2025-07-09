Here's a full, one-piece specification of the app from beginning to end — clear, structured, and copy-paste ready for code generation:

---

# 📘 Project Spec: Large Book Chunking & Translation Tool

## 🎯 Overview

This tool is designed to process large text files (books) by:
1. Chunking the raw text into manageable pieces.
2. Processing each chunk (e.g., translation, summarization) using an LLM.
3. Repeating failed or incomplete chunks as needed.
4. Rebuilding the processed chunks into a final, complete output file (e.g., a translated book).

The system will use **plain JSON files** for all storage. No database. No web interface. Simple terminal-based usage with three scripts:
- `chunk.py`
- `process.py`
- `rebuild.py`

---

## 🧩 Step 1: Chunking Script (`chunk.py`)

### 📥 Input:
- A raw `.txt` file (e.g. `mybook.txt`)
- Desired chunk size (e.g. 1000 or 2000 characters)

### 📤 Output:
- A `chunked` JSON file (e.g. `mybook_chunked.json`) with structure:

```json
{
  "meta": {
    "book_id": "mybook",
    "chunk_size": 1000,
    "total_chunks": 42
  },
  "chunks": [
    {
      "index": 0,
      "text": "First 1000 characters of book...",
      "status": "pending",
      "result": null
    },
    {
      "index": 1,
      "text": "Next 1000 characters of book...",
      "status": "pending",
      "result": null
    },
    ...
  ]
}
````

---

## ⚙️ Step 2: Processing Script (`process.py`)

### 📥 Input:

* A `chunked` JSON file (from `chunk.py`)
* Prompt template (e.g., "Translate this to Spanish: {text}")
* Model name (e.g., "gpt-4", "claude-3")
* API key (via environment variable)

### 📤 Output:

* Updates the same JSON file with results
* Each chunk now has:

  * `status`: `"done"` or `"error"`
  * `result`: the processed text (if successful)
  * `error`: error message (if failed)

### 🔁 Processing behavior:

* Script ONLY processes chunks where `status != "done"`
* Each chunk tried only ONCE per run (no retries)
* **Saves JSON file after EVERY chunk processed** (immediately after each LLM call)
  - This ensures no progress is lost if the script crashes
  - Can safely Ctrl+C and resume later
  - Each save includes the latest result/error for that chunk
* Shows detailed progress bar with:
  - Current chunk number / Total chunks
  - Success count
  - Failed count  
  - Processing speed (chunks/min)
  - ETA based on current speed
  - Live status updates

Example progress display:
```
Processing: [████████░░░░░░░░░░░░] 42/100 chunks | ✓ 40 | ✗ 2 | Speed: 3.2/min | ETA: 18m 45s
```

---

## 🏗️ Step 3: Rebuilding Script (`rebuild.py`)

### 📥 Input:

* A `processed` JSON file (from `process.py`)

### 📤 Output:

* A final `.txt` file (e.g. `mybook_translated_final.txt`)
* Concatenates all `result` values in chunk order
* Shows summary of build:
  - Total chunks rebuilt
  - Any missing chunks (errors/pending)
  - Output file size

---

## ✅ Summary of Scripts

### `chunk.py`

* Input: `raw_book.txt`
* Output: `chunked.json`
* Job: Split into fixed-size chunks

### `process.py`

* Input: `chunked.json`
* Output: `processed.json`
* Job: Process (translate/summarize/etc.) each chunk using an LLM

### `rebuild.py`

* Input: `processed.json`
* Output: `final_output.txt`
* Job: Combine all results into a final readable file

---

## 📋 Usage Examples

```bash
# Step 1: Chunk a book into 2000 character pieces
python chunk.py mybook.txt --chunk-size 2000

# Step 2: Process chunks with translation (can be run multiple times)
python process.py mybook_chunked.json --prompt "Translate to Spanish: {text}" --model gpt-4

# If some chunks failed, just run again - it will only process failed/pending chunks:
python process.py mybook_chunked.json --prompt "Translate to Spanish: {text}" --model gpt-4

# Step 3: Rebuild into final file
python rebuild.py mybook_chunked.json -o mybook_spanish.txt
```

## 📊 Progress Tracking

The process.py script provides real-time progress information:

```
Starting processing of mybook_chunked.json
Found 100 chunks: 95 pending, 5 already done

Processing: [████████░░░░░░░░░░░░] 42/95 chunks | ✓ 40 | ✗ 2 | Speed: 3.2/min | ETA: 16m 33s
Current: Processing chunk 42 - "It was the best of times, it was the..."

Summary:
- Total chunks: 100
- Successfully processed: 45
- Failed: 2 (chunks: 23, 67)
- Already done: 5
- Processing time: 14m 3s
```

## 🔧 Notes

* All data stored in simple JSON files
* **Progress saved after EVERY LLM call** (completely crash-safe)
* Can interrupt processing at any time without losing work
* Easy to inspect and manually edit chunks
* Simple design allows for future enhancements

---

**This system is designed for simplicity and iteration. Build fast, improve later.**

