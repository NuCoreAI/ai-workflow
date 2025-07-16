#configuration file for defaults
import os


class AIConfig:
    def __init__(self, data_path:str=None, models_path:str=None):
        self.__data_path__:str = data_path if data_path else "../../examples"
        self.__models_path__:str = models_path if models_path else "../../../models"
        self.__profile_file__ = "profile.json"
        self.__nodes_file__ = "nodes.xml"
        self.__ragdb_file__ = "ragdb"
        self.__llm_model__ = "qwen2.5-coder-3b.gguf" #"qwen3-1.7b",
        self.__llm_reranker_model__ = "bge-reranker-v2-m3.gguf"
        self.__embedding_model__ = "all-miniLM-L6-v2.gguf"

        self.__model_host__="localhost"
        self.__model_port__=8013
        self.__model_url__=f"http://{self.__model_host__}:{self.__model_port__}/v1/chat/completions"

        self.__reranker_host__="localhost"
        self.__reranker_port__=8026
        self.__reranker_url__=f"http://{self.__reranker_host__}:{self.__reranker_port__}/v1/rerank"

        self.__embedding_host__="localhost"
        self.__embedding_port__=8052
        self.__embedding_url__=f"http://{self.__embedding_host__}:{self.__embedding_port__}/v1/embeddings"



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
