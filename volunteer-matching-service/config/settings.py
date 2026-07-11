from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AnyHttpUrl natively allows localhost without a top-level domain (TLD)
    backend_base_url: AnyHttpUrl = "http://localhost:5000"
    campaign_endpoint: str = "/api/campaign/"
    users_endpoint: str = "/api/user"
    vector_store_dir: str = "./vector_store"
    top_n_candidates: int = 50
    top_k_recommendations: int = 10
    embedding_model_name: str = "sentence-transformers/paraphrase-mpnet-base-v2"

    class Config:
        env_file = ".env"
