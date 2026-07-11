from fastapi import FastAPI, HTTPException

from config.settings import Settings
from models.volunteer import Volunteer
from pipeline import RecommendationPipeline

app = FastAPI()
settings = Settings()
service = RecommendationPipeline(settings)


@app.get("/")
def read_root():
    return {"message": "Volunteer matching service is online."}


@app.get("/recommend/{campaign_id}")
def recommend(campaign_id: str, use_dummy: bool = True):
    try:
        recommendations = service.recommend(campaign_id, use_dummy_data=use_dummy)
        volunteer_ids = [item["volunteer_id"] for item in recommendations]
        return {"campaign_id": campaign_id, "volunteer_ids": volunteer_ids, "recommendations": recommendations}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/embedding/sync")
def sync_embedding(volunteer: Volunteer):
    try:
        embedding = service.embedding_generator.generate_volunteer_embedding(volunteer)
        service.vector_store.upsert_volunteer_embedding(embedding)
        return {"detail": "Volunteer embedding synced", "volunteer_id": embedding.volunteer_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
