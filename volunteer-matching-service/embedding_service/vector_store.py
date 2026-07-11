from __future__ import annotations
import math
from typing import Dict, List, Any
from config.settings import Settings
from models.embedding import VolunteerEmbedding


class VectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        # Pure Python fallback dictionary to completely bypass broken native C++ binaries
        self._mock_db: Dict[str, Dict[str, Any]] = {}
        print("[DEBUG] Using Pure-Python Fallback Vector Store to bypass Windows system conflicts.")

    def persist(self) -> None:
        """No-op kept for backwards compatibility."""
        return None

    def upsert_volunteer_embedding(self, embedding: VolunteerEmbedding) -> None:
        """Saves the volunteer embedding inside a pure Python dictionary layer."""
        if isinstance(embedding.skills, list):
            skills_text = ", ".join(str(skill) for skill in embedding.skills)
        else:
            skills_text = str(embedding.skills)

        document_payload = f"Volunteer ID: {embedding.volunteer_id} | Location: {embedding.location} | Skills: {skills_text}"

        # Standard clean storage mapping
        self._mock_db[str(embedding.volunteer_id)] = {
            "id": str(embedding.volunteer_id),
            "embedding": list(embedding.embedding),
            "document": document_payload
        }

    def query_similar_volunteers(self, query_embedding: List[float], top_n: int) -> List[Dict]:
        """Performs a standard pure-Python Cosine/Euclidean similarity math score extraction."""
        if not self._mock_db:
            return []

        scored_candidates = []

        # Simple Euclidean Distance tracking math loop
        for v_id, record in self._mock_db.items():
            v_emb = record["embedding"]
            
            # Basic distance vector check calculation
            if len(v_emb) == len(query_embedding):
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(v_emb, query_embedding)))
            else:
                dist = 0.0
                
            scored_candidates.append({
                "volunteer_id": v_id,
                "text": record["document"],
                "distance": dist
            })

        # Sort closest first (smallest distance value represents highest similarity)
        scored_candidates.sort(key=lambda x: x["distance"])
        return scored_candidates[:top_n]

    def delete_volunteer_embedding(self, volunteer_id: str) -> None:
        if str(volunteer_id) in self._mock_db:
            del self._mock_db[str(volunteer_id)]
