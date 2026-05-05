# Commands

## Install Command
```bash
python -m venv venv
source venv/bin/activate
pip install -e . -r requirements.txt
```

## Start Commands
The project is driven by the `main.py` CLI. You must run it from the directory containing your data (e.g., `data/test_set/`).

**Process Questions (End-to-End Inference):**
```bash
python ../../main.py process-questions --config max_nst_o3m
```
*(Other configs available: `base`, `pdr`, `max`, `max_no_ser_tab`, `ibm_llama70b`, etc.)*

## Build Command
None (Python script execution).

## Test Command
```bash
pytest tests/
```

## Pipeline Stages Commands
**Download Docling Models:**
```bash
python main.py download-models
```

**Parse PDFs:**
```bash
python main.py parse-pdfs --parallel --chunk-size 2 --max-workers 10
```

**Serialize Tables:**
```bash
python main.py serialize-tables --max-workers 10
```

**Process Reports (Ingestion):**
```bash
python main.py process-reports --config ser_tab
```

## Lint / Format Commands
Not explicitly configured.
