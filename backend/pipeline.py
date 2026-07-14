import os
import shutil
import logging
from typing import List, Optional
from backend.config import settings
from backend.document_loader import load_text
from backend.chunking import chunk_text
from backend.embeddings import Embedder
from backend.vector_store import VectorStore
from backend.retriever import Retriever
from backend.judge import Judge
from backend.llm import LLMGenerator
from backend.healer import Healer, HealingAction
from backend.metrics_store import MetricsStore
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self):
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(settings.VECTOR_DB_PATH) or ".", exist_ok=True)

        self.embedder = Embedder()
        dummy_emb = self.embedder.embed(["test"])[0]
        self.dim = dummy_emb.shape[0]

        self.vector_store_path = settings.VECTOR_DB_PATH
        try:
            if os.path.exists(f"{self.vector_store_path}.index"):
                self.vector_store = VectorStore.load(self.vector_store_path, self.dim)
            else:
                self.vector_store = VectorStore(dimension=self.dim)
        except Exception as e:
            logger.warning(f"Failed to load vector store ({e}). Starting fresh.")
            self.vector_store = VectorStore(dimension=self.dim)
            for ext in [".index", ".meta"]:
                try:
                    os.remove(f"{self.vector_store_path}{ext}")
                except:
                    pass

        self.retriever = Retriever(self.embedder, self.vector_store)
        self.judge = Judge(settings.JUDGE_MODEL_NAME)
        self.llm = LLMGenerator(settings.LLM_MODEL_NAME)
        self.healer = Healer()
        self.metrics = MetricsStore()
        self.current_documents = []

    def index_document(self, file_path: str) -> int:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        dest = os.path.join(settings.DATA_DIR, os.path.basename(file_path))
        if not os.path.exists(dest):
            shutil.copy(file_path, dest)
        file_path = dest

        try:
            text = load_text(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read document: {e}")

        chunks = chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
            strategy=settings.CHUNK_STRATEGY
        )
        logger.info(f"Generated {len(chunks)} chunks for {os.path.basename(file_path)}")
        if not chunks:
            return 0

        embeddings = self.embedder.embed(chunks)
        metadatas = [{"text": chunk, "source": file_path, "chunk_index": i} for i, chunk in enumerate(chunks)]
        self.vector_store.add_embeddings(embeddings, metadatas)
        self.vector_store.save(self.vector_store_path)
        if file_path not in self.current_documents:
            self.current_documents.append(file_path)
        return len(chunks)

    def reindex_all(self):
        self.vector_store = VectorStore(dimension=self.dim)
        for doc_path in self.current_documents:
            self.index_document(doc_path)
        self.vector_store.save(self.vector_store_path)

    def query(self, user_query: str, top_k: Optional[int] = None) -> dict:
        if top_k is None:
            top_k = settings.TOP_K

        # Retrieve
        retrieval_results = self.retriever.retrieve(user_query, top_k=top_k)
        chunks_text = [r["text"] for r in retrieval_results]

        # Log top retrieved chunks for debugging
        if chunks_text:
            logger.info(f"Top 3 chunks for query '{user_query}':")
            for i, chunk in enumerate(chunks_text[:3]):
                logger.info(f"  [{i+1}] (first 100 chars): {chunk[:100]}...")

        # Judge
        if chunks_text:
            judge_scores = self.judge.score(user_query, chunks_text)
            avg_score = float(np.mean(judge_scores))
        else:
            judge_scores = []
            avg_score = 0.0

        for i, res in enumerate(retrieval_results):
            res["relevance"] = judge_scores[i] if i < len(judge_scores) else None

        # Healing
        healing_actions = self.healer.evaluate_and_heal(avg_score)
        healed = len(healing_actions) > 0

        if healed:
            self.reindex_all()
            retrieval_results = self.retriever.retrieve(user_query, top_k=top_k)
            chunks_text = [r["text"] for r in retrieval_results]
            if chunks_text:
                judge_scores = self.judge.score(user_query, chunks_text)
                avg_score = float(np.mean(judge_scores))
                for i, res in enumerate(retrieval_results):
                    res["relevance"] = judge_scores[i] if i < len(judge_scores) else None
            else:
                avg_score = 0.0

        # ------ RELAXED BUT GROUNDED PROMPT ------
        if not chunks_text:
            answer = "No text could be extracted from the document. Please check the file."
        else:
            # Use top 8 chunks to broaden context
            context = "\n\n".join(chunks_text[:8])
            prompt = (
                "You are an AI that answers questions based on the provided context. "
                "Try to extract an answer from the context if at all possible. "
                "If the context is incomplete, give your best attempt and mention what you could find. "
                "Only if the context is completely unrelated to the question, say: 'The document does not seem to contain information about this.'\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {user_query}\n"
                "Answer:"
            )
            answer = self.llm.generate(prompt)

        self.metrics.add(user_query, avg_score, top_k, healed)

        return {
            "query": user_query,
            "answer": answer,
            "retrieved_chunks": [
                {
                    "text": r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"],
                    "score": r["score"],
                    "relevance": r.get("relevance")
                }
                for r in retrieval_results
            ],
            "avg_relevance": avg_score,
            "threshold": settings.RELEVANCE_THRESHOLD,
            "healed": healed,
            "healing_actions": [a.to_dict() for a in healing_actions]
        }