from pathlib import Path

"""
Tool definitions for Static Information Retrieval
Converts static information from text files into RAG chunks suitable for use in AI workflows/embeddings.
The static information is formatted with a title, category, content, and exmaples. They are separated by "---end chuck---".
"""
from ai_iox_workflow.config import AIConfig
from ai_iox_workflow.rag.rag_data_struct import RAGData
from ai_iox_workflow.rag.rag_formatter import RAGFormatter


class StaticInfoRAGFormatter(RAGFormatter):
    def __init__(self, indent_str: str = "    ", prefix: str = ""):
        """
        Initialize the formatter with the path to the tools JSON file.
        """

    def format(self, **kwargs):
        """
        Convert the formatted tools into a list of RAG documents.
        Each document contains an ID, category, and content.
        :param static_info_path if provided if not the default from config will be used.
        """
        static_info_path=kwargs["static_info_path"] if "static_info_path" in kwargs else AIConfig().getStaticInfoPath()

        if not Path(static_info_path).exists():
            raise FileNotFoundError(f"Static info file not found: {static_info_path}")
        
        #now, go through the static info directory, read each file, and then convert into RAGData
        static_info_path = Path(static_info_path)

        # If it's a directory, read all files in the directory
        static_rag = RAGData() 
        for file in static_info_path.glob("*.rag"):
            with open(file, "r") as f:
                content = f.read()
                # Split the content by "---end chuck---" to separate different chunks
                chunks = content.split("---end chuck---")
                for chunk in chunks:
                    if chunk.strip():
                        # get the type and category from the chunk
                        lines = chunk.strip().split("\n")
                        if len(lines) >= 2:
                            name = lines[0].strip()
                            doc_type = lines[1].strip()
                            category = lines[2].strip()
                            static_rag.add_document(chunk.strip(), [], name, {"type": doc_type, "category": category})

        return static_rag 

