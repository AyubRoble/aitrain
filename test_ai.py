from sentence_transformers import SentenceTransformer
import pickle
import json
import re
from difflib import get_close_matches

print("🔍 Webtoon Recommendation Engine v3.0")

# Load data
try:
    print("📚 Loading AI model and data...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    with open('webtoon_embeddings.pkl', 'rb') as f:
        webtoon_embeddings = pickle.load(f)

    with open('webtoon_detailed_analysis.json', 'r') as f:
        webtoon_data = json.load(f)
    
    print(f"✅ Loaded {len(webtoon_data)} webtoons successfully!")

except Exception as e:
    print(f"❌ Error loading data: {str(e)}")
    exit(1)

def extract_title(query):
    """Extract title from query with better matching"""
    query = query.lower()
    # Remove common phrases
    clean_query = query.replace('i like ', '').replace('similar to ', '').replace('something like ', '').strip()
    
    # Find closest matching title
    titles = [title.lower() for title in webtoon_data.keys()]
    matches = get_close_matches(clean_query, titles, n=1, cutoff=0.6)
    
    if matches:
        # Find the original title with correct capitalization
        for title in webtoon_data.keys():
            if title.lower() == matches[0]:
                return title
    return None

def get_best_recommendation(query):
    """Get the best recommendation based on user query"""
    try:
        # Extract the reference title
        reference_title = extract_title(query)
        
        if not reference_title or reference_title not in webtoon_data:
            print(f"\n❌ Couldn't find the webtoon you mentioned. Please check the title.")
            return
            
        # Get reference webtoon's characteristics
        reference_webtoon = webtoon_data[reference_title]
        reference_genres = reference_webtoon['analysis']['genre_categories']
        reference_elements = reference_webtoon['analysis'].get('story_elements', [])
        
        # Create rich context for matching
        context = f"{reference_title} {' '.join(reference_genres)} {' '.join(reference_elements)}"
        query_embedding = model.encode(context)
        
        # Find similar webtoons
        similarities = []
        for title, embedding in webtoon_embeddings.items():
            if title == reference_title:
                continue
                
            score = query_embedding.dot(embedding)
            
            # Boost score for matching genres and elements
            webtoon = webtoon_data[title]
            matching_genres = set(reference_genres) & set(webtoon['analysis']['genre_categories'])
            matching_elements = set(reference_elements) & set(webtoon['analysis'].get('story_elements', []))
            
            score += len(matching_genres) * 0.05
            score += len(matching_elements) * 0.03
            
            if score > 0.3:
                similarities.append((score, title))
        
        similarities.sort(reverse=True)
        
        if not similarities:
            print("\n❌ No good matches found. Try a different query!")
            return
        
        best_score, best_title = similarities[0]
        webtoon = webtoon_data[best_title]
        
        print(f"\n🎯 If you like {reference_title}, you'll love:")
        print("-" * 50)
        print(f"📚 Title: {best_title}")
        print(f"⭐ Match Score: {(best_score * 100):.1f}%")
        print(f"🎭 Genres: {', '.join(webtoon['analysis']['genre_categories'])}")
        print(f"💫 Elements: {', '.join(webtoon['analysis'].get('story_elements', []))}")
        print(f"🖼️ Image: {webtoon['basic_info']['image_url']}")
        print(f"📖 Synopsis: {webtoon['content']['synopsis'][:150]}...")
        
        # Explain the recommendation
        matching_genres = set(reference_genres) & set(webtoon['analysis']['genre_categories'])
        matching_elements = set(reference_elements) & set(webtoon['analysis'].get('story_elements', []))
        
        if matching_genres or matching_elements:
            print("\n💡 Why this match?")
            if matching_genres:
                print(f"- Similar genres: {', '.join(matching_genres)}")
            if matching_elements:
                print(f"- Similar elements: {', '.join(matching_elements)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("\n🚀 Ready to recommend! Try queries like:")
    print("- 'I like Eleceed'")
    print("- 'Something like Solo Leveling'")
    print("- 'Similar to Tower of God'")
    
    while True:
        try:
            query = input("\n🔍 What kind of webtoon are you looking for? (or 'q' to quit): ")
            if query.lower() == 'q':
                break
            if not query.strip():
                continue
                
            get_best_recommendation(query)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using the recommendation engine!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()