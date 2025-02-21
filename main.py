from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendation_engine import WebtoonRecommender

app = FastAPI()
recommender = WebtoonRecommender()

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/recommend")
def get_recommendation(query: Query):
    result = recommender.get_recommendation(query.query)
    return result