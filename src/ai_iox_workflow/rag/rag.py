# rag processor

import json
import chromadb
import requests
from ai_iox_workflow.config import AIConfig
from ai_iox_workflow.rag.rag_data_struct import RAGData


class RAGProcessor:
    def __init__(self, collection_name, db_path=None, base_url=None, username=None, password=None):
        self.config = AIConfig()
        self.db = chromadb.PersistentClient(path=self.config.getCollectionPersistencePath(collection_name, db_path)) 
        self.collection = self.db.get_or_create_collection(collection_name)
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
                print(f"Error: {response.status_code} - {response.text} - data size = {len(document)}")
                return None
            result = response.json()
            if "data" not in result:
                print("No embedding found in response")
                return None
            data = result["data"][0]
            if "embedding" not in data:
                print("No embedding key in data")
                return None
            embedding = data["embedding"]
            if not isinstance(embedding, list):
                print("No embedding key in data")
                return None
            if len(embedding) == 0:
                print("Embedding is empty")
                return None
            
            # Convert to float if necessary
            embedding_result = [float(x) for x in embedding]
            return embedding_result
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    def add_update(self, collection_data:RAGData):
        """
            adds to the collection to the collection with its embedding and metadata
        """
        if not collection_data or not isinstance(collection_data, RAGData):
            raise ValueError("Collection data must be a non-empty dictionary")

        if "documents" not in collection_data or "embeddings" not in collection_data or "metadatas" not in collection_data:
            raise ValueError("Collection data must contain 'documents', 'embeddings', and 'metadatas' keys")  

        if len(collection_data["documents"]) == 0 or len(collection_data["embeddings"]) == 0 or len(collection_data["ids"])== 0:
            print("Nothing changed ... ")
            return 


        return self.collection.upsert(
            documents=collection_data["documents"],
            ids=collection_data.get("ids", []),
            embeddings=collection_data["embeddings"],
            metadatas=collection_data["metadatas"]
        )

    def __compare_documents__(self, collection_data:RAGData):
        """
        Compares the collection data with the existing collection.
        Returns a dictionary with the differences.
        """
        if not collection_data or not isinstance(collection_data, RAGData):
            raise ValueError("Collection data must be a non-empty dictionary")

        if "documents" not in collection_data or "ids" not in collection_data or "metadatas" not in collection_data:

            raise ValueError("Collection data must contain 'documents', 'ids', and 'metadatas' keys")   

        existing_collection = self.collection.get(ids=None, include=["documents", "metadatas"])
        existing_ids = existing_collection.get("ids", [])

        
        new_ids = set(collection_data.get("ids", []))
        existing_ids_set = set(existing_ids)
        added_ids = new_ids - existing_ids_set
        unchanged_indexes = []
        removed_ids = existing_ids_set - new_ids

        for existing_id in existing_ids:
            existing_assets = self.collection.get(ids=[existing_id], include=["documents", "metadatas"])
            if not existing_assets or len(existing_assets["documents"]) == 0:
                print(f"ID {existing_id} exists in the collection but has no associated documents")
                continue

            existing_document= existing_assets["documents"][0]

            index=0
            for id in collection_data["ids"]:
                if id == existing_id:
                    if collection_data["documents"][index] == existing_document:
                        unchanged_indexes.append(index)
                        break
                index += 1

        return {
            "added": list(added_ids),
            "unchanged": unchanged_indexes,
            "removed": list(removed_ids)
        }
    
    def compare_documents_update_collection(self, documents:RAGData):
        """
        Compare the documents in the collection with the provided documents.
        Returns a dictionary with added, changed, and removed IDs.
        Those that removed or changed will be updated in the collection.
        """
        if not documents or not isinstance(documents, RAGData):
            raise ValueError("Documents must be a non-empty list")
        
        results = self.__compare_documents__(documents)
        if not results:
            print("No results found in the collection")
            return None
        
        #don't care about added
        # added = results.get("added") 
        unchanged = results.get("unchanged") 
        removed = results.get("removed")

        if removed and len(removed) > 0:
            self.remove(removed)

        result: RAGData = RAGData() 

        for i in range(len(documents["ids"])):
            if i in unchanged:
                continue
            doc_content = documents["documents"][i]
            embedding = self.embed_document(doc_content)
            if embedding:
                result["documents"].append(doc_content)
                result["embeddings"].append(embedding)
                result["metadatas"].append(documents["metadatas"][i])
                result["ids"].append(documents["ids"][i])

        return self.add_update(result)


    def query(self, query_text:str, n_results:int=5):
        """
        Queries the collection with the given text and returns the top n results.
        """
        if not query_text:
            raise ValueError("Query text cannot be empty")

        query_embedding = self.embed_document(query_text)
        if not query_embedding:
            print("Failed to embed query text")
            return None

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        if not results or "documents" not in results or len(results["documents"]) == 0:
            print("No results found")
            return None
        
        return results["documents"]

