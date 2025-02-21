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
async def recommend(query: Query):
    try:
        print("Starting recommendation process...")
        import numpy as np  # Try importing here to see specific error
        print("Numpy imported successfully")
        
        recommendations = engine.get_recommendations(query.query)
        return {"status": "success", "recommendations": recommendations}
    except ImportError as e:
        print(f"Import Error details: {str(e)}")
        return {"status": "error", "message": f"Detailed Import Error: {str(e)}"}
    except Exception as e:
        print(f"General Error details: {str(e)}")
        return {"status": "error", "message": f"Detailed Error: {str(e)}"}