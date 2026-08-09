# 🔬 ECE Lab Assistant — BIT Mesra
### AI-powered offline lab guide · Semesters 1–8 · EC24102 and beyond

---

## The Plan (one paragraph)
Build a JSON database of all 80 ECE experiments → RAG pipeline retrieves the right
experiment for any student query → LLM generates the response → fine-tune Phi-3-mini
on the QA pairs in August on free Colab GPU → swap in the local model → completely
offline system that runs on any laptop with zero API cost.

---

## Current Status

| Layer | Status |
|---|---|
| JSON schema | ✅ Designed |
| Sem 1 experiments (8 exps) | ✅ Complete |
| RAG retriever (TF-IDF + FAISS) | ✅ Built |
| QA pair generator | ✅ Built — 385 pairs from 8 exps |
| Streamlit frontend (3 modes) | ✅ Built |
| LLM backends (Groq/Gemini/Ollama) | ✅ Wired |
| Phi-3 fine-tuning script | ✅ Ready for Colab |
| Sem 2–8 experiments | 🔲 Add your lab manual content |

---

## Project Structure

```
AI_assistant_IOT/
│
├── backend/
│   ├── main.py                  ← FastAPI entry point
│   ├── routers/
│   └── services/
│
├── data/
│   ├── experiments/              ← one JSON per semester/lab
│   │   └── sem1_EC24102_basic_electronics.json
│   ├── qa_pairs/
│   │   ├── training_pairs.jsonl  ← Phi-3 fine-tuning data
│   │   └── training_pairs.json
│   ├── faiss_index.bin           ← auto-generated semantic index
│   └── index_meta.pkl
│
├── rag/
│   ├── retriever.py              ← FAISS + TF-IDF experiment retrieval
│   └── generator.py             ← multi-backend LLM response generator
│
├── models/
│   └── phi3_finetuned/          ← fine-tuned adapter goes here
│
├── frontend/
│   └── app.py                   ← Streamlit UI (theory/procedure/diagnosis)
│
├── scripts/
│   ├── generate_qa_pairs.py     ← JSON → training pairs
│   └── finetune_phi3.py         ← LoRA fine-tuning (run on Colab)
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/ece-lab-assistant
cd AI_assistant_IOT
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` — add at least one AI key:

```
# Free, 14,400 req/day — recommended starting point
GROQ_API_KEY=your_groq_key_here

# For photo analysis only
GEMINI_API_KEY=your_gemini_key_here
```

Get Groq key free at: https://console.groq.com (no credit card)

```bash
# Run the assistant
streamlit run frontend/app.py
```

---

## The 3 Modes

**📖 Theory** — Pre-lab reading. Shows aim, theory summary, formulas, key concepts,
components list. AI gives a deeper conceptual explanation on demand.

**🔧 Procedure** — During the experiment. Step-by-step guide, observation table format,
expected results, common errors as expandable warnings.

**🩺 Diagnosis** — After something goes wrong. Student types symptom + measured values.
System matches known fault patterns from JSON (instant, no API) then AI provides
specific breadboard fix instructions. Optional: upload circuit photo for Gemini Vision.

**🎓 Viva Prep** — Pre-exam. Shows all viva Q&A from JSON, plus AI handles follow-up
questions the examiner might ask.

---

## AI Cost Architecture

```
Student query
      ↓
Static DB match? ─── YES ──→ Answer (₹0, 0ms)
      │ NO
      ↓
Ollama running? ──── YES ──→ Local Phi-3 (₹0, offline, ~2s)
      │ NO
      ↓
Groq key set? ─────  YES ──→ Llama-3.1-8b (₹0, 14,400/day free)
      │ NO
      ↓
Gemini key set? ──── YES ──→ Flash (₹0 but 1500/day limit)
      │ NO
      ↓
Raw context only     (always works, no AI)
```

Photo analysis → Gemini Vision only (no local alternative yet)

---

## Adding More Experiments

Each JSON file in `data/experiments/` is one semester/lab.
Follow the schema in `schema.json` exactly.

```bash
# After adding new JSON files:
python scripts/generate_qa_pairs.py   # regenerate training data
python -c "from rag.retriever import get_retriever; get_retriever().build(force=True)"
```

### Schema fields (all required)
```json
{
  "id":           "sem2_EC24202_exp1_short_name",
  "semester":     2,
  "lab_code":     "EC24202",
  "lab_name":     "Analog Electronics Lab",
  "exp_number":   1,
  "title":        "Full experiment title",
  "aim":          "One sentence aim.",
  "theory":       { "summary", "key_formulas", "key_concepts" },
  "components":   [ { "name", "spec", "quantity" } ],
  "procedure":    [ "Step 1...", "Step 2..." ],
  "observations": { "table_headers", "sample_row", "what_to_plot" },
  "expected_results": { "description", "typical_values" },
  "common_errors":    [ { "symptom", "causes", "fix" } ],
  "circuit_diagnosis_hints": [ "hint1", "hint2" ],
  "viva_questions":   [ { "q", "a" } ]
}
```

---

## Phase 2 — Fine-tune Phi-3-mini (August, Colab)

**Step 1:** Add all 80 experiments from your lab manuals to `data/experiments/`
```bash
python scripts/generate_qa_pairs.py   # generates ~4000 QA pairs
```

**Step 2:** Upload to Google Colab
- `data/qa_pairs/training_pairs.jsonl`
- `scripts/finetune_phi3.py`

**Step 3:** Run fine-tuning (~2-3 hours on free T4 GPU)
```python
!python finetune_phi3.py
```

**Step 4:** Download the LoRA adapter, convert to GGUF, load into Ollama
```bash
ollama create ece-assistant -f Modelfile
# Set OLLAMA_MODEL=ece-assistant in .env
```

**Result:** Completely offline AI assistant, no internet, no API, no tokens.
Runs on any student laptop. Zero marginal cost per query.

---

## Why This Architecture

| Concern | Solution |
|---|---|
| Token cost with 30 students | Groq free tier (14,400/day) handles it |
| No internet in lab | Ollama + local Phi-3 after fine-tuning |
| Wrong answers | RAG grounds every response in JSON context |
| Photo analysis | Gemini Vision (1 call per session, limited) |
| Scaling to 8 semesters | Just add JSON files — no code changes |

---

## Papers / Presentations

This project covers:
- **RAG pipeline** (retrieval-augmented generation)
- **LoRA fine-tuning** on domain-specific data
- **Multi-backend LLM orchestration**
- **Offline AI deployment** with Ollama
- **Synthetic QA generation** from structured data
- Applied to a real problem in your own college


---

*Built by Sarbajit Ghosh,ECE BIT Mesra.*
