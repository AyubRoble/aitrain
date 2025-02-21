from sentence_transformers import SentenceTransformer
import pickle
import json
import re
from fuzzywuzzy import fuzz
from difflib import get_close_matches
import random

class WebtoonRecommender:
    def __init__(self):
        print("🚀 Initializing Webtoon Recommendation Engine...")
        self.load_data()
        self.previous_recommendations = set()
        
    def load_data(self):
        """Load model and data"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            with open('webtoon_embeddings.pkl', 'rb') as f:
                self.webtoon_embeddings = pickle.load(f)
                
            with open('webtoon_detailed_analysis.json', 'r') as f:
                self.webtoon_data = json.load(f)
                
            print(f"✅ Loaded {len(self.webtoon_data)} webtoons successfully!")
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

    def detect_format(self, webtoon_data):
        """Detect if content is manga/manhwa/manhua"""
        # Check type field
        type_lower = webtoon_data['basic_info']['type'].lower()
        if 'manga' in type_lower:
            return 'manga'
        elif 'manhwa' in type_lower:
            return 'manhwa'
        elif 'manhua' in type_lower:
            return 'manhua'
        
        # Check alternative titles for language hints
        alt_titles = webtoon_data['basic_info'].get('alternative_titles', '')
        if 'japanese' in str(alt_titles).lower():
            return 'manga'
        elif 'korean' in str(alt_titles).lower():
            return 'manhwa'
        elif 'chinese' in str(alt_titles).lower():
            return 'manhua'
        
        # Default to manhwa (colored format)
        return 'manhwa'

    def find_by_description(self, description):
        """Find content based on description with format awareness"""
        format_keywords = {
            'manga': ['manga', 'japanese'],
            'manhwa': ['manhwa', 'korean', 'webtoon'],
            'manhua': ['manhua', 'chinese']
        }
        
        genre_keywords = {
            'funny': ['comedy', 'humor', 'funny', 'hilarious'],
            'action': ['action', 'fighting', 'battle', 'martial arts'],
            'romance': ['romance', 'love', 'relationship'],
            'dark': ['dark', 'horror', 'thriller'],
            'fantasy': ['fantasy', 'magic', 'supernatural']
        }

        description_lower = description.lower()
        
        # Check if format is specified
        requested_format = None
        for format_type, keywords in format_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                requested_format = format_type
                break

        # Find matching genres
        requested_genres = []
        for genre, keywords in genre_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                requested_genres.append(genre.title())

        # Filter matches
        matching_titles = []
        for title, data in self.webtoon_data.items():
            # Format check
            current_format = self.detect_format(data)
            if requested_format and current_format != requested_format:
                continue
            if not requested_format and current_format == 'manga':
                continue  # Default to colored unless manga specifically requested
                
            # Genre check
            if requested_genres:
                if not any(genre in data['analysis']['genre_categories'] 
                          for genre in requested_genres):
                    continue
                    
            matching_titles.append(title)
        
        return random.choice(matching_titles) if matching_titles else None

    def get_recommendation(self, query):
        """Main recommendation function"""
        try:
            query = query.lower().strip()
            
            # Handle descriptive queries first
            if not any(title.lower() in query for title in self.webtoon_data.keys()):
                description_match = self.find_by_description(query)
                if description_match:
                    query = f"like {description_match}"

            # Extract title if present
            title_patterns = [
                r'(?:like|similar to|enjoy) (.+?)(?:\s|$)',
                r'(?:hate|dislike|don\'t like) (.+?)(?:\s|$)',
            ]
            
            reference_title = None
            for pattern in title_patterns:
                if match := re.search(pattern, query):
                    potential_title = match.group(1).strip()
                    matches = get_close_matches(
                        potential_title.lower(),
                        [t.lower() for t in self.webtoon_data.keys()],
                        n=1,
                        cutoff=0.6
                    )
                    if matches:
                        reference_title = next(t for t in self.webtoon_data.keys() 
                                            if t.lower() == matches[0])
                    break

            if not reference_title:
                matches = get_close_matches(
                    query,
                    [t.lower() for t in self.webtoon_data.keys()],
                    n=1,
                    cutoff=0.6
                )
                if matches:
                    reference_title = next(t for t in self.webtoon_data.keys() 
                                        if t.lower() == matches[0])

            if not reference_title:
                return {
                    'status': 'error',
                    'message': "Try being more specific or mention a title you like!"
                }

            # Get reference content
            reference = self.webtoon_data[reference_title]
            reference_format = self.detect_format(reference)
            
            # Calculate similarities
            scores = []
            reference_context = (
                f"{reference_title} "
                f"{' '.join(reference['analysis']['genre_categories'])} "
                f"{' '.join(reference['analysis'].get('story_elements', []))}"
            )
            reference_embedding = self.model.encode(reference_context)
            
            is_negative = any(word in query for word in ['hate', 'dislike', 'don\'t like'])
            
            for title, embedding in self.webtoon_embeddings.items():
                if title == reference_title or title in self.previous_recommendations:
                    continue
                
                # Format check
                current_format = self.detect_format(self.webtoon_data[title])
                if current_format != reference_format:
                    continue
                    
                # Base similarity
                score = float(reference_embedding.dot(embedding))
                
                # Adjust score based on genres and elements
                candidate = self.webtoon_data[title]
                matching_genres = set(reference['analysis']['genre_categories']) & set(candidate['analysis']['genre_categories'])
                matching_elements = set(reference['analysis'].get('story_elements', [])) & set(candidate['analysis'].get('story_elements', []))
                
                if is_negative:
                    score = 1 - score
                else:
                    score += len(matching_genres) * 0.05
                    score += len(matching_elements) * 0.03
                
                if score > 0.3:  # Quality threshold
                    scores.append((score, title))
            
            if not scores:
                return {
                    'status': 'error',
                    'message': 'No good matches found. Try a different query!'
                }
            
            # Get best match
            best_score, best_title = max(scores, key=lambda x: x[0])
            recommended = self.webtoon_data[best_title]
            
            # Add to previous recommendations
            self.previous_recommendations.add(best_title)
            
            return {
                'status': 'success',
                'recommendation': {
                    'title': best_title,
                    'score': best_score,
                    'format': self.detect_format(recommended),
                    'genres': recommended['analysis']['genre_categories'],
                    'elements': recommended['analysis'].get('story_elements', []),
                    'image_url': recommended['basic_info']['image_url'],
                    'synopsis': recommended['content']['synopsis']
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}'
            }

if __name__ == "__main__":
    # Direct testing interface
    recommender = WebtoonRecommender()
    print("\n🎮 Ready to recommend! Try:")
    print("- 'Funny manga'")
    print("- 'Action webtoon'")
    print("- 'Something like Solo Leveling'")
    print("- 'Chinese martial arts'")
    
    while True:
        try:
            query = input("\n🔍 What are you looking for? (or 'q' to quit): ")
            if query.lower() == 'q':
                break
            if not query.strip():
                continue
            
            result = recommender.get_recommendation(query)
            
            if result['status'] == 'success':
                rec = result['recommendation']
                print(f"\n✨ Found something for you!")
                print("-" * 50)
                print(f"📚 Title: {rec['title']}")
                print(f"📖 Format: {rec['format'].title()}")
                print(f"⭐ Match Score: {(rec['score'] * 100):.1f}%")
                print(f"🎭 Genres: {', '.join(rec['genres'])}")
                if rec['elements']:
                    print(f"💫 Elements: {', '.join(rec['elements'])}")
                print(f"🖼️ Image: {rec['image_url']}")
                print(f"📖 Synopsis: {rec['synopsis'][:150]}...")
            else:
                print(f"\n❌ {result['message']}")
                
        except KeyboardInterrupt:
            print("\n👋 Happy reading!")
            break
        except Exception as e:
            print(f"\n⚠️ Oops! {str(e)}")