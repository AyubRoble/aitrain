# convert_data.py
import pickle
import numpy as np
import json

print("Starting conversion...")

# Load and save embeddings in numpy format
print("Loading pickle file...")
with open('webtoon_embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)
print("Saving as .npy...")
np.save('webtoon_embeddings.npy', embeddings)
print("Conversion complete!")