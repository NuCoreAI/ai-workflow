#configuration file for defaults
import os


class AIConfig:
    def __init__(self, data_path:str=None, models_path:str=None):
        self.__data_path__:str = data_path if data_path else "../examples"
        self.__models_path__:str = models_path if models_path else "../../models"
        self.__profile_file__ = "profile.json"
        self.__nodes_file__ = "nodes.xml"
        self.__llm_model__ = "llama-3.1-8b" #"qwen3-1.7b",
        self.__llm_reranker_model__ = "bge-reranker-v2-m3"

    def getProfile(self, file:str):
        if not file:
            file = self.__profile_file__

        return os.path.join(self.__data_path__, file)

    def getNodes(self, file:str):
        if not file:
            file = self.__nodes_file__

        return os.path.join(self.__data_path__, file)

    def getLLMModel(self, model:str):
        if not model:
            model = self.__llm_model__

        return os.path.join(self.__models_path__, model)

    def getRerankerModel(self, model:str):
        if not model:
            model = self.__llm_reranker_model__

        return os.path.join(self.__models_path__, model)
    


