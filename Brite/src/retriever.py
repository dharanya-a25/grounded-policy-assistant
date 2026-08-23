import os
import numpy as np

# Set local cache directory for HuggingFace before importing sentence_transformers
# to avoid Access Denied / file lock errors on Windows global cache.
os.environ["HF_HOME"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.hf_cache'))
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from sentence_transformers import SentenceTransformer
from src.parser import parse_manual, parse_amendment

class Retriever:
    def __init__(self, manual_path, amendment_path=None):
        self.base_clauses = parse_manual(manual_path)
        self.amd_clauses = parse_amendment(amendment_path) if amendment_path else {}
        self.all_clauses = {**self.base_clauses, **self.amd_clauses}
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.clause_ids = list(self.all_clauses.keys())
        self.clause_texts = list(self.all_clauses.values())
        
        self.embeddings = self.model.encode(self.clause_texts, convert_to_tensor=False, show_progress_bar=False)
        
    def retrieve(self, query, top_k=7, include_amendment=True):
        import re
        clean_query = re.sub(r'for a claim (dated|in).*?(2026|\d{4})', '', query, flags=re.IGNORECASE)
        clean_query = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', '', clean_query, flags=re.IGNORECASE)
        clean_query = clean_query.strip()
        
        query_emb = self.model.encode([clean_query], show_progress_bar=False)[0]
        # Calculate cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        scores = np.dot(self.embeddings, query_emb) / norms
        
        top_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in top_indices:
            c_id = self.clause_ids[idx]
            # Filter out amendment clauses if include_amendment is False
            if not include_amendment and c_id.startswith("Amendment"):
                continue
                
            results.append({
                "id": c_id,
                "text": self.all_clauses[c_id],
                "score": float(scores[idx])
            })
            if len(results) >= top_k:
                break
                
        return results

if __name__ == "__main__":
    r = Retriever("policy-manual.md")
    res = r.retrieve("What is the resource limit?")
    for c in res:
        print(c["id"], c["score"])
