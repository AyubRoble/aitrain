from sentence_transformers import SentenceTransformer
import json
import numpy as np
import pickle

print("🚀 Starting AI training...")

# Load your webtoon data
with open('webtoon_detailed_analysis.json', 'r') as f:
    webtoon_data = json.load(f)
    print(f"📚 Loaded {len(webtoon_data)} webtoons")

# Initialize the model
print("🤖 Initializing AI model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings for each webtoon
print("💫 Creating embeddings...")
webtoon_embeddings = {}
for title, info in webtoon_data.items():
    # Combine relevant info for better matching
    text = f"{title} {info['content']['synopsis']} {' '.join(info['analysis']['genre_categories'])}"
    embedding = model.encode(text)
    webtoon_embeddings[title] = embedding
    
    # Progress indicator
    if len(webtoon_embeddings) % 100 == 0:
        print(f"⏳ Processed {len(webtoon_embeddings)} webtoons...")

# Save the trained embeddings
print("💾 Saving trained data...")
with open('webtoon_embeddings.pkl', 'wb') as f:
    pickle.dump(webtoon_embeddings, f)

print("✅ AI Training Complete!")
print(f"📊 Processed {len(webtoon_embeddings)} webtoon titles")