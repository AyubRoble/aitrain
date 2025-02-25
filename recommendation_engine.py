# recommendation_engine.py
import numpy as np
import json
from sentence_transformers import SentenceTransformer

class RecommendationEngine:
    def __init__(self):
        self.model = self.load_model()
        self.embeddings, self.webtoons = self.load_data()

    def load_model(self):
        print("Loading model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model

    def load_data(self):
        print("Loading data...")
        embeddings = np.load('webtoon_embeddings.npy')
        with open('webtoon_detailed_analysis.json', 'r') as f:
            webtoons = json.load(f)
        return embeddings, webtoons

    def get_recommendations(self, query):
        query_embedding = self.model.encode([query])[0]
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-5:][::-1]
        recommendations = []
        for idx in top_indices:
            recommendations.append(self.webtoons[idx])
        return recommendations