from __future__ import annotations

from typing import List

from models.candidate import Candidate
from models.embedding import CampaignEmbedding
from embedding_service.vector_store import VectorStore


class CandidateRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    @staticmethod
    def _cosine_similarity(distance: float) -> float:
        # For normalized embeddings, Chroma returns a distance that can be converted to cosine similarity.
        return max(0.0, 1.0 - distance)

    def retrieve(self, campaign_embedding: CampaignEmbedding, top_n: int) -> List[Candidate]:
        raw_results = self.vector_store.query_similar_volunteers(campaign_embedding.embedding, top_n)
        candidates: List[Candidate] = []
        for raw in raw_results:
            candidates.append(
                Candidate(
                    volunteer_id=raw["volunteer_id"],
                    similarity_score=self._cosine_similarity(raw["distance"]),
                    metadata={},
                )
            )
        return sorted(candidates, key=lambda candidate: candidate.similarity_score, reverse=True)
