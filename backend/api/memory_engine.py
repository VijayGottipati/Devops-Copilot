from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pgvector.django import L2Distance
from .models import AgentMemory, Project
import os

def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.environ.get('GEMINI_API_KEY')
    )

def store_memory(project_id, content_text):
    project = Project.objects.get(id=project_id)
    embeddings_model = get_embeddings_model()
    
    # Generate 768-dimensional vector from Gemini
    embedded_vector = embeddings_model.embed_query(content_text)
    
    memory = AgentMemory.objects.create(
        project=project,
        content=content_text,
        embedding=embedded_vector
    )
    return memory

def retrieve_persona_context(project_id, query_text, limit=3):
    """Retrieve the most relevant past manager stylistic feedback."""
    project = Project.objects.get(id=project_id)
    embeddings_model = get_embeddings_model()
    
    query_vector = embeddings_model.embed_query(query_text)
    
    # Use pgvector L2 (Euclidean) distance to find most similar vectors
    similar_memories = AgentMemory.objects.filter(project=project) \
                                          .order_by(L2Distance('embedding', query_vector))[:limit]
    
    context = "\n".join([mem.content for mem in similar_memories])
    return context
