from __future__ import annotations

from typing import List

from models.candidate import Candidate
from models.recommendation import Recommendation


class Reranker:
    def rank(self, candidates: List[Candidate], top_k: int) -> List[Recommendation]:
        ranked = sorted(candidates, key=lambda item: item.final_score, reverse=True)
        recommendations: List[Recommendation] = []
        for candidate in ranked[:top_k]:
            reason = self._build_reason(candidate)
            recommendations.append(
                Recommendation(
                    volunteer_id=candidate.volunteer_id,
                    similarity_score=candidate.similarity_score,
                    business_score=candidate.business_score,
                    final_score=candidate.final_score,
                    reason=reason,
                    metadata=candidate.metadata,
                )
            )
        return recommendations

    @staticmethod
    def _build_reason(candidate: Candidate) -> str:
        components = [
            f"Similarity {candidate.similarity_score:.2f}",
            f"Business {candidate.business_score:.2f}",
        ]
        return "; ".join(components)
