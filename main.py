from fastapi import FastAPI
from pydantic import BaseModel
from recommendation_engine import RecommendationEngine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the recommendation engine
engine = RecommendationEngine()

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/recommend")
async def recommend(query: Query):
    try:
        print("Starting recommendation process...")
        recommendations = engine.get_recommendations(query.query)
        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        print(f"General Error details: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"}