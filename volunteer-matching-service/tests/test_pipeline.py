import unittest

from config.settings import Settings
from pipeline import RecommendationPipeline


class PipelineTests(unittest.TestCase):
    def test_recommendation_pipeline_with_dummy_data(self):
        settings = Settings()
        pipeline = RecommendationPipeline(settings)
        recommendations = pipeline.recommend("camp1", use_dummy_data=True)

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), settings.top_k_recommendations)
        for recommendation in recommendations:
            self.assertIn("volunteer_id", recommendation)
            self.assertIn("final_score", recommendation)


if __name__ == "__main__":
    unittest.main()
