# 📧 Email Recap Tool (Local / Offline)

Automatically reads `.eml` files from a folder, analyzes each email using a **local Qwen3 model**, and exports a clean summary to Excel.

**100% offline — no data leaves your machine.**

## What It Does

- Parses `.eml` files (sender, subject, date, body)
- Uses a local Qwen3 model via LM Studio to extract keywords and write a short summary
- Exports everything to a formatted `.xlsx` file

## Output Columns

| Column | Description |
|---|---|
| Mailbox | Email address of the sender |
| Subject | Email subject |
| Date | Date sent |
| Keywords | Important keywords extracted by AI |
| Summary | Short 1–2 sentence summary of the email |

---

## Requirements

- macOS (tested on MacBook Air M2)
- Python 3.10+
- [LM Studio](https://lmstudio.ai) installed with a Qwen3 model downloaded

---

## Setup

### 1. Install LM Studio & download the model

1. Download [LM Studio](https://lmstudio.ai)
2. Open LM Studio → Search for `Qwen3-8B` (recommended for M2)
3. Download the **Q4_K_M** variant (good balance of speed vs quality on M2)
4. Load the model → go to **Local Server** tab → click **Start Server**

> LM Studio will serve the model at `http://localhost:1234`

### 2. Set the model name in the code

Open `src/ai_analyzer.py` and update this line to match the model name shown in LM Studio:

```python
MODEL_NAME = "qwen3-8b"  # ← change this to match your LM Studio model name
```

### 3. Install Python dependencies

```bash
cd email-recap
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## How To Run

### Step 1 — Put your `.eml` files into `data/emails/`

```
data/
└── emails/
    ├── invoice_june.eml
    ├── meeting_notes.eml
    └── ...
```

### Step 2 — Make sure LM Studio server is running

LM Studio → Local Server tab → **Start Server** (green button)

### Step 3 — Run the script

```bash
python src/main.py
```

### Step 4 — Open the output

```
outputs/email_recap.xlsx
```

---

## Project Structure

```
email-recap/
├── README.md               # This file
├── .gitignore
├── requirements.txt        # openai, openpyxl
├── src/
│   ├── main.py             # Entry point — runs the full pipeline
│   ├── eml_reader.py       # Parses .eml files into structured data
│   ├── ai_analyzer.py      # Calls local Qwen model for keywords + summary
│   └── excel_writer.py     # Writes results to formatted .xlsx
└── data/
    └── emails/             # Drop your .eml files here
```

---

## Example Output

| Mailbox | Subject | Date | Keywords | Summary |
|---|---|---|---|---|
| vendor@supplier.com | Invoice #1042 | 2024-06-01 | invoice, payment, due date | Vendor sent invoice #1042 for $2,400 due by June 15. |
| hr@company.com | Annual Leave Policy | 2024-06-03 | leave, policy, HR, approval | HR updated the annual leave policy, requiring 2-week prior approval. |

---

## Notes

- Recommended model for M2: *qwen3.5-9b** (~5GB RAM, fast enough for batch processing)
- Email body is trimmed to 3000 characters before sending to the model (saves processing time)
- Qwen3's "thinking mode" output (`<think>...</think>`) is automatically stripped
- No API key, no internet connection needed
