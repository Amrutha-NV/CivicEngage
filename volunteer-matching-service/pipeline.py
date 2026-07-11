from __future__ import annotations
from typing import Dict, Any, List, Optional, Callable

from config.settings import Settings
from embedding_service.embedding_generator import EmbeddingGenerator
from embedding_service.vector_store import VectorStore
from fetching_service.campaign_fetcher import CampaignFetcher
from fetching_service.volunteer_fetcher import VolunteerFetcher
from candidate_generation_service.retriever import CandidateRetriever
from business_rule_service.rule_engine import RuleEngine
from business_rule_service.availability_rule import AvailabilityRule
from business_rule_service.verification_rule import VerificationRule
from business_rule_service.max_campaign_rule import MaxCampaignRule
from scoring_service.scorer import Scorer
from scoring_service.weight_config import get_weights_for_category
from reranking_service.reranker import Reranker
from utils.pipeline_context import PipelineContext


class RecommendationPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fetch_campaigner = CampaignFetcher(settings)
        self.fetch_volunteer = VolunteerFetcher(settings)
        self.embedding_generator = EmbeddingGenerator(settings)
        self.vector_store = VectorStore(settings)
        self.candidate_retriever = CandidateRetriever(self.vector_store)
        self.rule_engine = RuleEngine([
            AvailabilityRule(),
            VerificationRule(),
            MaxCampaignRule(max_active_campaigns=2),
        ])
        self.reranker = Reranker()
        
        # Explicit declaration fixes the "Attribute 'scorer' is unknown" type checker error.
        # This can be set externally or dynamically resolved inside the execution loop.
        self.scorer: Optional[Scorer] = None

    def recommend(
        self, 
        campaign_id: str, 
        use_dummy_data: bool = False,
        stage_callback: Optional[Callable[[str, Any], None]] = None
    ) -> list[dict]:
        """
        Executes the full end-to-end recommendation workflow.
        Provides a real-time tracking mechanism through the optional stage_callback parameter.
        """
        
        # Internal helper to safely trigger step inspection hooks
        def trigger_stage_trace(stage_name: str, payload: Any) -> None:
            if stage_callback:
                stage_callback(stage_name, payload)

        context = PipelineContext()

        # === STAGE 1: Fetch Stage ===
        if use_dummy_data:
            context.campaign = self.fetch_campaigner.fetch_campaign_dummy(campaign_id)
            context.volunteers = self.fetch_volunteer.fetch_volunteers_dummy()
        else:
            context.campaign = self.fetch_campaigner.fetch_campaign(campaign_id)
            context.volunteers = self.fetch_volunteer.fetch_volunteers()
            
        trigger_stage_trace("1_fetch", {
            "campaign": context.campaign,
            "volunteers": context.volunteers
        })

        # === STAGE 2: Embedding Stage ===
        context.campaign_embedding = self.embedding_generator.generate_campaign_embedding(context.campaign)
        
        volunteer_embeddings = []
        for volunteer in context.volunteers:
            volunteer_embedding = self.embedding_generator.generate_volunteer_embedding(volunteer)
            self.vector_store.upsert_volunteer_embedding(volunteer_embedding)
            volunteer_embeddings.append(volunteer_embedding)
            
        trigger_stage_trace("2_embedding", {
            "campaign_embedding": context.campaign_embedding,
            "volunteer_embeddings": volunteer_embeddings
        })

        # === STAGE 3: Candidate Generation Stage ===
        candidates = self.candidate_retriever.retrieve(
            context.campaign_embedding, 
            self.settings.top_n_candidates
        )
        trigger_stage_trace("3_candidate_generation", candidates)

        # === STAGE 4: Business Rule Stage ===
        filtered_candidates = self.rule_engine.apply(
            context.campaign, 
            candidates, 
            context.volunteers
        )
        trigger_stage_trace("4_business_rules", filtered_candidates)

        # === STAGE 5: Scoring Stage ===
        # Use instance scorer if assigned; otherwise, construct locally based on the campaign's domain category
        current_scorer = self.scorer
        if current_scorer is None:
            weights = get_weights_for_category(context.campaign.category)
            current_scorer = Scorer(weights)
            
        scored_candidates = current_scorer.score_candidates(
            context.campaign, 
            filtered_candidates, 
            context.volunteers
        )
        trigger_stage_trace("5_scoring", scored_candidates)

        # === STAGE 6: Re-ranking Stage ===
        recommendations = self.reranker.rank(
            scored_candidates, 
            self.settings.top_k_recommendations
        )
        trigger_stage_trace("6_reranking", recommendations)

        # === Final Output Parsing ===
        final_output = [recommendation.model_dump() for recommendation in recommendations]
        trigger_stage_trace("7_final_output", final_output)

        return final_output
