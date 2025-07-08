Here's a full, one-piece specification of the app from beginning to end — clear, structured, and copy-paste ready for code generation:

---

````markdown
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
- Optional chunk overlap (e.g. 100 characters) to maintain context
- Processing configuration (task type, target language, model, etc.)
- Optional metadata (e.g. book title, language)

### 📤 Output:
- A `chunked` JSON file (e.g. `mybook_chunked.json`) with structure:

```json
{
  "meta": {
    "book_id": "mybook",
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "language": "en",
    "title": "My Book",
    "processing_config": {
      "task": "translate",
      "target_language": "es",
      "model": "gpt-4",
      "api_key_env": "OPENAI_API_KEY",
      "max_retries": 3,
      "retry_delay": 5
    }
  },
  "chunks": [
    {
      "index": 0,
      "start": 0,
      "end": 1000,
      "text": "First 1000 characters of book...",
      "prompt": "Translate the following English text to Spanish, maintaining the style and tone:\n\n{text}",
      "status": "pending",
      "result": null,
      "error": null,
      "retry_count": 0,
      "last_attempt": null
    },
    ...
  ]
}
````

---

## ⚙️ Step 2: Processing Script (`process.py`)

### 📥 Input:

* A `chunked` JSON file (from `chunk.py`)
* Task type: `"translate"`, `"summarize"`, or custom
* (Optional) Target language or other parameters

### 📤 Output:

* A `processed` JSON file (e.g. `mybook_translated.json`)
* Each chunk has:

  * `status`: `"done"`, `"error"`, or `"pending"`
  * `result`: the result of processing (e.g., translated text)
  * `error`: error message if failed
  * `retry_count`: number of retry attempts
  * `last_attempt`: timestamp of last processing attempt

### 🔁 Re-run logic:

* Script skips chunks where `status == "done"`
* Only re-processes `pending` or `error` chunks
* Respects `max_retries` limit per chunk
* Implements exponential backoff for rate limiting
* Saves progress after each chunk to enable resumability
* Useful for retrying failures or continuing partial runs

---

## 🏗️ Step 3: Rebuilding Script (`rebuild.py`)

### 📥 Input:

* A `processed` JSON file (from `process.py`)

### 📤 Output:

* A final `.txt` file (e.g. `mybook_translated_final.txt`)
* Concatenates all `result` values in chunk order
* Can optionally check that all chunks have `status == "done"` before building
* Handles overlapping chunks intelligently to avoid duplication
* Generates a summary report of any failed chunks

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

## 🔧 Implementation Details

### Chunking Strategy:
* Use character-based chunking with configurable overlap
* Overlap ensures context continuity between chunks
* Smart splitting at sentence/paragraph boundaries when possible

### Error Handling:
* Comprehensive error tracking per chunk
* Automatic retry with exponential backoff
* Rate limit detection and handling
* Progress saved after each chunk for crash recovery

### Prompt Management:
* Each chunk includes a customizable prompt template
* Prompts can use placeholders like `{text}`, `{chunk_index}`, `{total_chunks}`
* Default prompts provided for common tasks (translate, summarize)

## 📋 Usage Examples

```bash
# Chunk a book with 2000 char chunks and 200 char overlap
python chunk.py --input mybook.txt --chunk-size 2000 --overlap 200 --task translate --target-lang es

# Process with custom prompt
python process.py --input mybook_chunked.json --prompt "Summarize this text in 3 sentences: {text}"

# Rebuild with validation
python rebuild.py --input mybook_processed.json --validate --output final.txt
```

## 🔧 Notes

* All data is stored in human-readable JSON.
* You can inspect, edit, or retry any chunk manually if needed.
* Progress is automatically saved, making the process resumable.
* Later enhancements could include:

  * CLI menu
  * GUI
  * Parallel processing
  * Model/version tracking
  * Output in other formats (Markdown, HTML)
  * Multiple LLM provider support

---

**This system is designed for simplicity and iteration. Build fast, improve later.**

