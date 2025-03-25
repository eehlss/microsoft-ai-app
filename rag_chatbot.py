import os
import faiss
import numpy as np
from openai import OpenAI
import json
from medical_knowledge import MEDICAL_KNOWLEDGE

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Failed to initialize OpenAI client: {str(e)}")

def load_embeddings_and_index():
    """Load pre-trained embeddings and FAISS index"""
    try:
        # Load the pre-computed embeddings
        embeddings = np.load("attached_assets/embeddings.npy")
        # Load the FAISS index
        index = faiss.read_index("attached_assets/faiss_index.index")
        # Load chunks for context retrieval
        with open("attached_assets/chunks.json", 'r') as f:
            chunks = json.load(f)
        print("Successfully loaded pre-trained embeddings and index")
        return True, index, embeddings, chunks
    except Exception as e:
        print(f"Warning: Could not load pre-trained embeddings: {str(e)}")
        return False, None, None, None

def initialize_default_index():
    """Initialize index with default medical knowledge"""
    try:
        # Get embeddings for medical knowledge
        embeddings = []
        texts = []

        for entry in MEDICAL_KNOWLEDGE:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=entry
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            texts.append(entry)

        # Create FAISS index
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings, dtype='float32'))

        print("Successfully initialized default knowledge base")
        return index, texts
    except Exception as e:
        print(f"Error initializing default index: {str(e)}")
        return None, MEDICAL_KNOWLEDGE

# Initialize both knowledge sources
use_pretrained, pretrained_index, pretrained_embeddings, chunks = load_embeddings_and_index()
default_index, default_texts = initialize_default_index()

def get_relevant_context(query, use_pretrained_first=True):
    """Get relevant context from either pre-trained or default knowledge base"""
    try:
        # Get query embedding
        query_response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = query_response.data[0].embedding

        # Try pre-trained index first if available and requested
        if use_pretrained_first and use_pretrained and pretrained_index is not None:
            try:
                k = 3  # Number of relevant passages to retrieve
                D, I = pretrained_index.search(np.array([query_embedding], dtype='float32'), k)
                relevant_texts = [chunks[i]["chunk"] for i in I[0]]
                return "\n".join(relevant_texts)
            except Exception as e:
                print(f"Warning: Error using pre-trained index: {str(e)}. Falling back to default knowledge base.")

        # Use default index as fallback
        if default_index is not None:
            k = 3
            D, I = default_index.search(np.array([query_embedding], dtype='float32'), k)
            relevant_texts = [default_texts[i] for i in I[0]]
            return "\n".join(relevant_texts)
        else:
            # Ultimate fallback to raw medical knowledge
            return "\n".join(MEDICAL_KNOWLEDGE[:3])

    except Exception as e:
        print(f"Warning: Error in similarity search: {str(e)}. Using default knowledge base.")
        return "\n".join(MEDICAL_KNOWLEDGE[:3])

def get_chatbot_response(question):
    """Generate response using relevant context"""
    try:
        # Get relevant context using RAG
        context = get_relevant_context(question)

        # Create prompt with context
        prompt = f"""
        Using the following medical information about hemoglobinopathies:
        {context}

        Please answer this question in a clear and informative way:
        {question}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical expert helping explain hemoglobinopathies to patients and their families."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error getting chatbot response: {str(e)}")