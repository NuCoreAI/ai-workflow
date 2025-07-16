# rag processor

import json
import chromadb
import requests
from ai_iox_workflow.config import AIConfig


class RAGProcessor:
    def __init__(self, db_path=None, base_url=None, username=None, password=None):
        self.config = AIConfig()
        self.db = chromadb.Client()
        self.collection = self.db.create_collection("iox_rag_docs")
        self.username = username if username else "admin"
        self.password = password if password else "admin"

    def embed_document(self, document:str):
        """
         embeds a document using the embedding model
        """
        if not document:
            raise ValueError("Document cannot be empty")
        
        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "input": document
        }

        try:
            response = requests.post(self.config.getEmbeddingURL(), headers=headers, data=json.dumps(body))
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                return None
            return response.json()
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    def embed_documents(self, documents:list):
        """
        embeds a list of documents using the embedding model
        """
        if not documents or not isinstance(documents, list):
            raise ValueError("Documents must be a non-empty list")
        
        embeddings = []
        for doc in documents:
            embedding = self.embed(doc)
            if embedding:
                embeddings.append(embedding)
        
        return embeddings


# Example RAG-friendly documents
#docs = [
#    {
#        "id": "doc1",
#        "content": """***Device***
#Name: Right Hue Color XY
#ID: ZB24569_011_108
#***Properties***
#- Color X: Range 0.0 to 1.0 (Color, step 1.0, precision 5)
#- Preferred Units: Enum [Kelvin, Mired]
#"""
#    },
#    {
#        "id": "doc2",
#        "content": """***Device***
#Name: Ecobee Thermostat
#ID: n002_t421800120477
#***Accepts Commands***
#- Heat Setpoint [CLISPH]
#    ▸ Parameter: 32–90°F by 1
#"""
#    }
#]
#
## Embed and insert
#collection.add(
#    documents=[doc["content"] for doc in docs],
#    embeddings=[model.encode(doc["content"]) for doc in docs],
#    ids=[doc["id"] for doc in docs],
#    metadatas=[{"name": doc["id"]} for doc in docs]
#)
