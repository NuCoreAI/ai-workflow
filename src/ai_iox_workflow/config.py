#configuration file for defaults
import os

DEFAULT_NUCORE_INSTALL_DIR = "workspace/nucore"
DEFAULT_AI_INSTALL_DIR_NAME= "ai-workflow"
DEFAULT_AI_INSTALL_DIR = os.path.join(DEFAULT_NUCORE_INSTALL_DIR, DEFAULT_AI_INSTALL_DIR_NAME)

class AIConfig:
    def __init__(self, install_dir:str=None, data_path:str=None, models_path:str=None):
        if not install_dir:
            install_dir = os.path.join(os.path.expanduser('~'), DEFAULT_NUCORE_INSTALL_DIR)
        self.__data_path__:str = data_path if data_path else os.path.join(install_dir, DEFAULT_AI_INSTALL_DIR_NAME, "examples")
        self.__models_path__:str = models_path if models_path else os.path.join(install_dir, "models")
        self.__profile_file__ = "profile.json"
        self.__nodes_file__ = "nodes.xml"
        self.__ragdb_file__ = "ragdb"
        self.__llm_model__ = "qwen2.5-coder-3b.gguf" #"qwen3-1.7b",
        self.__llm_reranker_model__ = "bge-reranker-v2-m3.gguf"
        self.__embedding_model__ = "Qwen3-Embedding-0.6B-f16.gguf"

        self.__model_host__="localhost"
        self.__model_port__=8013
        self.__model_url__=f"http://{self.__model_host__}:{self.__model_port__}/v1/chat/completions"

        self.__reranker_host__="localhost"
        self.__reranker_port__=8026
        self.__reranker_url__=f"http://{self.__reranker_host__}:{self.__reranker_port__}/v1/rerank"

        self.__embedding_host__="localhost"
        self.__embedding_port__=8052
        self.__embedding_url__=f"http://{self.__embedding_host__}:{self.__embedding_port__}/v1/embeddings"

        self.__collection_name_devices__ = "rag_docs_for_devices"

    def getCollectionNameForDevices(self):
        return self.__collection_name_devices__
    
    def getCollectionPersistencePath(self, collection_name:str, db_path:str=None):
        """
        Returns the path where the collection is stored.j
        """
        if db_path:
            return os.path.join(db_path, f"{collection_name}_db")

        return os.path.join(self.__data_path__, f"{collection_name}_db")

    def getProfile(self, file:str):
        if not file:
            file = self.__profile_file__

        return os.path.join(self.__data_path__, file)

    def getNodes(self, file:str=None):
        if not file:
            file = self.__nodes_file__

        return os.path.join(self.__data_path__, file)

    def getLLMModel(self, model:str=None):
        if not model:
            model = self.__llm_model__

        return os.path.join(self.__models_path__, model)

    def getRerankerModel(self, model:str=None):
        if not model:
            model = self.__llm_reranker_model__

        return os.path.join(self.__models_path__, model)
    
    def getEmbeddingModel(self, model:str=None):
        if not model:
            model = self.__llm_reranker_model__

        return os.path.join(self.__models_path__, model)

    def getModelURL(self):
        return self.__model_host__ 

    def getRerankerURL(self):
        return self.__reranker_url__    

    def getEmbeddingURL(self):
        return self.__embedding_url__

    def getRAGDB(self, file:str=None):
        if not file:
            return os.path.join(self.__data_path__, self.__ragdb_file__)

        return os.path.join(self.__data_path__, file)
