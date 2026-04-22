# Chapter 7 — File Handling and Automation Basics

Reading and writing files, automating tasks, and working with CSV and text data.

## Prerequisites

- Python 3.10+ installed
- Completed [Chapter 6](../6/) (OOP)

## The files

| # | File | Topic |
|---|------|-------|
| 1 | `reading_writing_files.py` | `open()`, `with`, read/write/append, `readlines`, `pathlib`, encoding |
| 2 | `automation.py` | Batch create/rename/move/copy/delete files, `os.walk`, logging to file |
| 3 | `csv_and_text.py` | `csv.reader`/`writer`, `DictReader`/`DictWriter`, TSV, text parsing, CSV-to-JSON |

## How to run

```bash
cd 7
python reading_writing_files.py
python automation.py
python csv_and_text.py
```

All generated files are placed in a `_output/` subfolder for easy cleanup:

```bash
rm -rf _output/
```

## Concepts introduced

### Reading and Writing Files
- `open(path, mode)` — `"r"`, `"w"`, `"a"`, `"x"`, `"rb"`, `"wb"`
- `with open(...) as f:` — automatic close
- `.read()`, `.readline()`, `.readlines()`
- `.write()`, `.writelines()`
- Appending to a file (`"a"` mode)
- `pathlib.Path` — `.name`, `.stem`, `.suffix`, `.parent`, `.exists()`, `.is_file()`
- Encoding: `encoding="utf-8"`

### Automating Repetitive Tasks
- `Path.mkdir()` — create folders
- `Path.glob()` — find files by pattern
- `Path.rename()` — batch rename
- `shutil.move()`, `shutil.copy2()` — move and copy
- `Path.unlink()` — delete a file
- `os.walk()` — walk a directory tree
- Timestamp logger — append lines with datetime
- Batch text replacement across files

### Working with CSV and Text Files
- `csv.reader` / `csv.writer` — basic row-based I/O
- `csv.DictReader` / `csv.DictWriter` — column names as keys
- Custom delimiters (TSV, semicolons)
- Processing: averages, filtering, writing subsets
- Parsing structured text (log files)
- `json.dump()` / `json.load()` — CSV-to-JSON conversion
- Word counting from a text file
