Here’s the updated **complete README.md** with your full name and title.

```markdown
# Self-Healing RAG Pipeline 🔧

A production‑grade **Retrieval‑Augmented Generation (RAG)** pipeline that automatically detects retrieval failures and **self‑heals** by adjusting chunking, embeddings, or retrieval strategy – no human intervention required.

> Built for reliability, not just demos. MLOps folks respect it because it actually tries to fix itself when things go wrong.

---

## ✨ Features

- 🔍 **Document ingestion** – upload `.pdf` and `.txt` files, automatically chunked and embedded.
- 🧠 **RAG Querying** – ask questions and get answers grounded in your documents.
- ⚖️ **Relevance Judge** – a lightweight cross‑encoder scores every retrieved chunk against the query.
- 🩺 **Auto‑Healing** – if average relevance drops below a threshold, the pipeline:
  - Re‑chunks (increase / decrease chunk size)
  - Switches embedding models
  - Changes chunking strategy (fixed → sentence‑based)
- 📈 **Real‑time Metrics** – chart of average relevance per query.
- 🗑️ **Reset Knowledge Base** – clear all documents and start fresh.
- 🎨 **Animated Intro** – personalised splash screen with your credit.
- 🌐 **Modern UI** – gradient backgrounds, glassmorphism cards, and smooth transitions.

---

## 🧱 Tech Stack

| Component        | Technology |
|------------------|------------|
| Backend          | Python, FastAPI |
| Vector Store     | FAISS (CPU) |
| Embeddings       | `all-mpnet-base-v2` (primary) + `all-MiniLM-L6-v2` (fallback) |
| Relevance Judge  | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Answer Generation| `google/flan-t5-large` (Seq2Seq) |
| Frontend         | HTML5, CSS3, JavaScript, Chart.js |
| Chunking         | Fixed‑size and sentence‑based with overlap |

---

## 📁 Project Structure

```
self_healing_rag/
├── backend/
│   ├── main.py            # FastAPI app & endpoints
│   ├── config.py          # All tunable parameters
│   ├── models.py          # Pydantic models
│   ├── chunking.py        # Text splitting logic
│   ├── embeddings.py      # Sentence‑Transformer wrapper
│   ├── vector_store.py    # FAISS wrapper
│   ├── retriever.py       # Embedding‑based retrieval
│   ├── judge.py           # Cross‑encoder relevance scorer
│   ├── healer.py          # Self‑healing strategies
│   ├── pipeline.py        # Core RAG logic (orchestrator)
│   ├── document_loader.py # PDF/TXT reader
│   ├── metrics_store.py   # In‑memory metric storage
│   └── llm.py             # LLM generator (Flan‑T5)
├── frontend/
│   ├── templates/
│   │   └── index.html     # Main UI
│   └── static/
│       ├── css/style.css  # Styling with intro animation
│       └── js/app.js      # Frontend logic, chart, reset
├── data/                  # Stored documents & vector store
├── requirements.txt
├── setup.py
├── run.py                 # Entry point
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd self_healing_rag
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> On Windows, if you encounter issues with `pydantic-core` or `faiss`, upgrade `pip` first:  
> `pip install --upgrade pip setuptools wheel`

### 4. Run the server
```bash
python run.py
```

### 5. Open the app
Go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

The first launch will download the models (~2 GB total) – please be patient.

---

## 🧑‍💻 Usage

1. You’ll see an animated intro – click anywhere to skip.
2. **Reset** the knowledge base (red button) to clear any old data.
3. **Upload** a PDF or TXT file by dragging & dropping or browsing.
4. **Type your question** in the input box and press **Ask**.
5. The answer appears, along with:
   - Average relevance score (and a colour‑coded bar).
   - List of retrieved chunks with similarity & judge scores.
6. If relevance is low, the system **heals** automatically – watch the healing log.

---

## ⚙️ Configuration

All adjustable parameters are in `backend/config.py`:

| Parameter               | Default                         | Description |
|-------------------------|---------------------------------|-------------|
| `CHUNK_SIZE`            | 400                             | Words per chunk |
| `CHUNK_OVERLAP`         | 100                             | Overlap between chunks |
| `CHUNK_STRATEGY`        | `"sentence"`                    | `"fixed"` or `"sentence"` |
| `EMBED_MODEL_NAME`      | `"all-mpnet-base-v2"`           | Primary embedding model |
| `JUDGE_MODEL_NAME`      | `"cross-encoder/ms-marco-MiniLM-L-6-v2"` | Relevance judge |
| `LLM_MODEL_NAME`        | `"google/flan-t5-large"`        | Answer generation model |
| `RELEVANCE_THRESHOLD`   | 0.25                            | Triggers healing if average < this |
| `TOP_K`                 | 15                              | Number of chunks to retrieve |

You can also update config on the fly via `POST /config` (see API below).

---

## 📡 API Endpoints

| Method | Endpoint         | Description |
|--------|------------------|-------------|
| `GET`  | `/`              | Main UI |
| `POST` | `/upload`        | Upload a document (multipart `file`) |
| `POST` | `/query`         | Ask a question (`{"query":"..."}`) |
| `POST` | `/reset`         | Clear all indexed documents |
| `GET`  | `/metrics`       | Get query relevance history |
| `GET`  | `/config`        | View current configuration |
| `POST` | `/config`        | Update configuration (partial) |
| `POST` | `/heal`          | Manually trigger healing |
| `GET`  | `/documents`     | List currently indexed documents |

---

## 🩺 How Self‑Healing Works

1. For every query, the **Judge** computes a relevance score (0–1) for each retrieved chunk.
2. If the **average** score falls below `RELEVANCE_THRESHOLD`, the **Healer** kicks in.
3. It cycles through predefined strategies (one per failure):
   - Increase chunk size → larger context
   - Decrease chunk size → finer granularity
   - Switch to the alternate embedding model
   - Switch chunking strategy (fixed ↔ sentence)
4. After healing, documents are **re‑indexed** and the query is retried.
5. A cooldown prevents repeated healing within 30 seconds.

This makes the pipeline robust against poorly chunked documents or embedding mismatches.

---

## 🖌️ Customisation

- **Change the intro credits**: edit the text inside `#intro-overlay` in `frontend/templates/index.html`.
- **Use a different LLM**: change `LLM_MODEL_NAME` in `config.py` (must be a Seq2Seq model like `t5-*` or `bart-*`).
- **Add more healing strategies**: extend the `HEALING_STRATEGIES` list and implement them in `healer.py`.

---

## 🐛 Troubleshooting

- **"The document does not contain this information"** – the retrieval truly found nothing. Try:
  - Uploading a different document.
  - Asking more specific questions using keywords from the text.
  - Check the terminal logs for retrieved chunk previews.
- **500 Internal Server Error** – likely a missing directory or corrupted vector store. Delete `data/vector_store*` and restart.
- **Slow first run** – models are being downloaded (one time). Subsequent starts are fast.

---

## 📜 License

MIT – feel free to use, modify, and distribute.

---

## 👨‍💻 Author

**Muhammad Anas Akhtar**  
AI Engineer  
"Building AI that learns, adapts, and improves."

---

*Happy self‑healing! If you find this useful, give it a ⭐ on GitHub.*
```
