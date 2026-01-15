"""
RAG Service for Vitrion
Provides retrieval-augmented generation for personalized health insights
using OpenAI embeddings and a curated knowledge base.
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

# OpenAI client
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    client = None
    print("Warning: OpenAI not installed. RAG features disabled.")

# Constants
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-4o-mini"  # Use mini for cost efficiency
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.json"


def embed_text(text: str) -> List[float]:
    """Generate embedding for a text using OpenAI ada-002"""
    if not client:
        return [0.0] * 1536  # Return zeros if no client
    
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_np = np.array(a)
    b_np = np.array(b)
    return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))


def load_knowledge_base() -> List[Dict]:
    """Load the pre-embedded knowledge base"""
    if not KNOWLEDGE_BASE_PATH.exists():
        return []
    
    with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def retrieve_relevant(
    query: str, 
    category: Optional[str] = None,
    top_k: int = 3
) -> List[Dict]:
    """
    Retrieve the most relevant documents from knowledge base.
    
    Args:
        query: The user's query or context
        category: Optional filter by category (sleep, energy, stress, etc.)
        top_k: Number of documents to retrieve
    
    Returns:
        List of relevant documents with similarity scores
    """
    knowledge_base = load_knowledge_base()
    if not knowledge_base:
        return []
    
    # Filter by category if specified
    if category:
        knowledge_base = [
            doc for doc in knowledge_base 
            if doc.get('category', '').lower() == category.lower()
        ]
    
    # Embed the query
    query_embedding = embed_text(query)
    
    # Calculate similarities
    results = []
    for doc in knowledge_base:
        if 'embedding' in doc and len(doc['embedding']) > 0:
            similarity = cosine_similarity(query_embedding, doc['embedding'])
            results.append({
                **doc,
                'similarity': similarity
            })
    
    # Sort by similarity and return top_k
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]


def generate_weekly_insight(
    mood_data: List[float],
    baseline: Dict,
    challenge_type: str = "general"
) -> Dict:
    """
    Generate personalized weekly insight using RAG.
    
    Args:
        mood_data: 7-day mood scores (1-10)
        baseline: User's baseline data (energy, sleep, stress)
        challenge_type: Type of challenge (sleep, energy, focus, stress)
    
    Returns:
        Dict with insight text and source citations
    """
    if not client:
        return {
            "insight": "AI 分析功能暫時無法使用。",
            "sources": []
        }
    
    # Analyze patterns
    avg_mood = sum(mood_data) / len(mood_data) if mood_data else 5
    baseline_energy = baseline.get('energy', 5)
    mood_change = avg_mood - baseline_energy
    
    # Find lowest day
    min_mood_idx = mood_data.index(min(mood_data)) if mood_data else 0
    day_names = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
    lowest_day = day_names[min_mood_idx % 7]
    
    # Create query for RAG
    if challenge_type == 'sleep':
        query = f"sleep quality mood energy correlation fatigue"
    elif challenge_type == 'energy':
        query = f"morning energy nutrition exercise productivity"
    elif challenge_type == 'focus':
        query = f"concentration productivity attention span cognitive"
    elif challenge_type == 'stress':
        query = f"stress cortisol relaxation mindfulness anxiety"
    else:
        query = f"mood energy wellbeing daily habits health"
    
    # Retrieve relevant research
    relevant_docs = retrieve_relevant(query, category=challenge_type, top_k=3)
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"研究：{doc['title']}\n來源：{doc['source']}\n摘要：{doc['abstract']}"
        for doc in relevant_docs
    ])
    
    # Generate insight with GPT
    prompt = f"""你是一個健康顧問 AI。根據用戶的週報數據和相關科學研究，提供個人化的洞察和建議。

用戶數據：
- 本週平均精神狀態：{avg_mood:.1f}/10
- 基線精神狀態：{baseline_energy}/10
- 變化：{'+' if mood_change >= 0 else ''}{mood_change:.1f}
- 最低點：{lowest_day}（{min(mood_data):.1f}分）
- 挑戰類型：{challenge_type}

相關研究：
{context if context else "暫無相關研究資料"}

請提供：
1. 對用戶本週狀態的分析（1-2句話）
2. 基於研究的一個具體建議
3. 如果有引用研究，請標註 [1], [2] 等

格式：直接輸出分析和建議，不要用標題或列表。保持 3-4 句話以內。使用繁體中文。"""

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是專業的健康顧問，提供科學 backed 的建議。使用繁體中文。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        insight_text = response.choices[0].message.content
        
        # Format sources
        sources = [
            {
                "id": idx + 1,
                "title": doc['title'],
                "source": doc['source']
            }
            for idx, doc in enumerate(relevant_docs)
        ]
        
        return {
            "insight": insight_text,
            "sources": sources,
            "stats": {
                "avg_mood": round(avg_mood, 1),
                "baseline_energy": baseline_energy,
                "mood_change": round(mood_change, 1),
                "lowest_day": lowest_day
            }
        }
        
    except Exception as e:
        return {
            "insight": f"分析時發生錯誤：{str(e)}",
            "sources": [],
            "stats": {}
        }


# Utility function to pre-embed knowledge base
def build_knowledge_base(articles: List[Dict]) -> None:
    """
    Embed articles and save to knowledge base.
    Call this once to build the knowledge base.
    
    Args:
        articles: List of dicts with title, source, abstract, category
    """
    embedded_articles = []
    
    for article in articles:
        # Create embedding from abstract
        text = f"{article['title']} {article['abstract']}"
        embedding = embed_text(text)
        
        embedded_articles.append({
            **article,
            "embedding": embedding
        })
        print(f"Embedded: {article['title']}")
    
    with open(KNOWLEDGE_BASE_PATH, 'w', encoding='utf-8') as f:
        json.dump(embedded_articles, f, ensure_ascii=False, indent=2)
    
    print(f"Knowledge base saved with {len(embedded_articles)} articles")
