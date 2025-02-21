from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendation_engine import WebtoonRecommender

app = FastAPI()
recommender = WebtoonRecommender()

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Webtoon Recommender API is running! 🚀"}

@app.post("/recommend")
def get_recommendation(query: Query):
    result = recommender.get_recommendation(query.query)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result