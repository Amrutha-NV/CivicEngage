from __future__ import annotations

from typing import Dict, List

from models.candidate import Candidate
from models.campaign import Campaign
from models.volunteer import Volunteer


class Scorer:
    def __init__(self, weight_config: Dict[str, float]):
        self.weights = weight_config

    def score_candidates(
        self,
        campaign: Campaign,
        candidates: List[Candidate],
        volunteers: List[Volunteer],
    ) -> List[Candidate]:
        volunteer_map = {v.id: v for v in volunteers}
        scored_candidates: List[Candidate] = []
        for candidate in candidates:
            volunteer = volunteer_map.get(candidate.volunteer_id)
            if volunteer is None:
                continue
            business_score = self._compute_business_score(candidate, volunteer)
            final_score = self._compute_final_score(candidate.similarity_score, business_score)
            candidate.business_score = business_score
            candidate.final_score = final_score
            scored_candidates.append(candidate)
        return scored_candidates

    def _compute_business_score(self, candidate: Candidate, volunteer: Volunteer) -> float:
        score = 0.0
        score += self.weights.get("attendance", 0.2) * volunteer.attendance_rate
        score += self.weights.get("availability", 0.1) * (1.0 if volunteer.availability else 0.0)
        score += self.weights.get("social_impact", 0.25) * volunteer.social_impact_score
        score += self.weights.get("verification", 0.15) * (1.0 if volunteer.verified else 0.0)
        score += self.weights.get("max_campaign", 0.1) * max(0.0, 1.0 - (volunteer.active_campaigns / 10.0))
        return min(1.0, score)

    def _compute_final_score(self, similarity_score: float, business_score: float) -> float:
        similarity_weight = self.weights.get("similarity", 0.4)
        business_weight = self.weights.get("business", 0.6)
        return similarity_weight * similarity_score + business_weight * business_score
