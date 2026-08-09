"""
rag/retriever.py
Loads all experiment JSONs → builds FAISS semantic index →
retrieves the most relevant experiment given a student query.

Two retrieval modes:
  1. Semantic  — sentence-transformers + FAISS (best quality)
  2. Keyword   — TF-IDF fallback (no GPU, fast, works offline)
"""

import os
import json
import glob
import pickle
import numpy as np
from typing import Optional

# ── Lazy detection for heavy ML libraries ─────────────────────────────────────
_SEMANTIC_CHECKED = False
_SEMANTIC_AVAILABLE = False

def is_semantic_available() -> bool:
    global _SEMANTIC_CHECKED, _SEMANTIC_AVAILABLE
    if not _SEMANTIC_CHECKED:
        try:
            import sentence_transformers  # type: ignore
            import faiss  # type: ignore
            _SEMANTIC_AVAILABLE = True
        except Exception:
            _SEMANTIC_AVAILABLE = False
        _SEMANTIC_CHECKED = True
    return _SEMANTIC_AVAILABLE

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "experiments")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index.bin")
META_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "index_meta.pkl")
EMBED_MODEL = "all-MiniLM-L6-v2"   # 80MB, runs on CPU fine


def _load_all_experiments() -> list[dict]:
    """Load every JSON file in data/experiments/. Each file is a list of experiments."""
    experiments = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                experiments.extend(data)
            else:
                experiments.append(data)
        except Exception as e:
            print(f"Warning: Failed to load experiment JSON from {path}: {e}")
    return experiments


def _experiment_to_text(exp: dict) -> str:
    """
    Convert one experiment dict to a single searchable text blob.
    This is what gets embedded / TF-IDFed.
    """
    parts = [
        exp.get("title", ""),
        exp.get("aim", ""),
        exp.get("theory", {}).get("summary", ""),
        " ".join(exp.get("theory", {}).get("key_concepts", [])),
        " ".join(exp.get("procedure", [])),
        " ".join(
            e.get("symptom", "") + " " + e.get("fix", "")
            for e in exp.get("common_errors", [])
        ),
        " ".join(
            qa.get("q", "") + " " + qa.get("a", "")
            for qa in exp.get("viva_questions", [])
        ),
        f"semester {exp.get('semester','')} {exp.get('lab_code','')} {exp.get('lab_name','')}",
    ]
    return " ".join(p for p in parts if p).lower()


class ExperimentRetriever:
    """
    Usage:
        r = ExperimentRetriever()
        r.build()                         # once — saves index to disk
        exp, score = r.retrieve("CE amplifier output clipping")
    """

    def __init__(self, use_semantic: bool = True):
        self.experiments: list[dict] = []
        self.texts: list[str] = []
        self.use_semantic = use_semantic
        self._model   = None
        self._index   = None
        self._tfidf   = None
        self._tfidf_matrix = None
        self._built   = False

    # ── build ─────────────────────────────────────────────────────────────
    def build(self, force: bool = False):
        """Build index from all JSON files. Saves to disk for fast reload."""
        if self._built and not force and len(self.experiments) > 0:
            return

        self.experiments = _load_all_experiments()
        if not self.experiments:
            print(f"  No experiments found in {DATA_DIR}. Indexing bypassed.")
            self._built = True
            return

        self.texts = [_experiment_to_text(e) for e in self.experiments]

        # Always build TF-IDF (lightweight, instant, always available)
        self._tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=8000)
        self._tfidf_matrix = self._tfidf.fit_transform(self.texts)

        # Lazy semantic FAISS setup
        if self.use_semantic and is_semantic_available():
            try:
                from sentence_transformers import SentenceTransformer
                import faiss
                if not force and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
                    self._index = faiss.read_index(INDEX_PATH)
                    with open(META_PATH, "rb") as f:
                        saved = pickle.load(f)
                    if saved.get("n") == len(self.experiments):
                        self._model = SentenceTransformer(EMBED_MODEL)
                        self._built = True
                        return

                self._model = SentenceTransformer(EMBED_MODEL)
                embeddings = self._model.encode(
                    self.texts, show_progress_bar=False, batch_size=32
                )
                embeddings = np.array(embeddings, dtype="float32")
                faiss.normalize_L2(embeddings)
                dim = embeddings.shape[1]
                self._index = faiss.IndexFlatIP(dim)   # inner product = cosine after normalise
                self._index.add(embeddings)
                try:
                    faiss.write_index(self._index, INDEX_PATH)
                    with open(META_PATH, "wb") as f:
                        pickle.dump({"n": len(self.experiments)}, f)
                except Exception:
                    pass
            except Exception as e:
                print(f"Semantic FAISS indexing failed or unavailable: {e}. Using TF-IDF fallback.")
                self._index = None
                self._model = None

        self._built = True

    # ── retrieve ──────────────────────────────────────────────────────────
    def retrieve(self, query: str, top_k: int = 1) -> list[tuple[dict, float]]:
        """
        Returns list of (experiment_dict, score) sorted by relevance.
        Falls back to TF-IDF if semantic index not available.
        """
        if not self.experiments:
            self.build()

        if not self.experiments:
            return []

        if self.use_semantic and self._index is not None and self._model is not None:
            try:
                import faiss
                q_emb = self._model.encode([query.lower()], convert_to_numpy=True).astype("float32")
                faiss.normalize_L2(q_emb)
                scores, indices = self._index.search(q_emb, top_k)
                return [(self.experiments[i], float(scores[0][j]))
                        for j, i in enumerate(indices[0]) if i >= 0]
            except Exception as e:
                print(f"FAISS search failed: {e}. Using TF-IDF fallback.")

        q_vec = self._tfidf.transform([query.lower()])
        sims  = cosine_similarity(q_vec, self._tfidf_matrix).flatten()
        top   = np.argsort(sims)[::-1][:top_k]
        return [(self.experiments[i], float(sims[i])) for i in top]

    def retrieve_one(self, query: str) -> tuple[Optional[dict], float]:
        results = self.retrieve(query, top_k=1)
        if results:
            return results[0]
        return None, 0.0

    def list_all(self) -> list[dict]:
        """Return lightweight list of all experiments (id, title, semester)."""
        if not self.experiments:
            self.build()
        return [
            {
                "id":       e["id"],
                "title":    e["title"],
                "semester": e.get("semester"),
                "lab_code": e.get("lab_code"),
            }
            for e in self.experiments
        ]


# ── singleton ─────────────────────────────────────────────────────────────────
_retriever: Optional[ExperimentRetriever] = None

def get_retriever() -> ExperimentRetriever:
    global _retriever
    if _retriever is None:
        _retriever = ExperimentRetriever()
        _retriever.build()
    return _retriever


if __name__ == "__main__":
    r = ExperimentRetriever()
    r.build(force=True)
    tests = [
        "CE amplifier output is clipping",
        "How to measure frequency using CRO",
        "Zener diode not regulating voltage",
        "BJT transistor characteristics beta",
        "op amp inverting gain formula",
        "logic gates NAND NOR truth table",
    ]
    print("\n-- Retrieval test ------------------------------")
    for q in tests:
        exp, score = r.retrieve_one(q)
        print(f"  Q: {q!r:50s}  -> {exp['title']!r}  (score={score:.3f})")
