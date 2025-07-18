import json
from pathlib import Path

"""
Tool definitions for RAG (Retrieval-Augmented Generation) processing.
Converts tools from a JSON file into RAG chunks suitable for use in AI workflows/embeddings.
The tools are formatted with a title, content, and examples, which can be used to enhance the context for AI models.
"""
from ai_iox_workflow.config import AIConfig

class ToolsRAGFormatter:
    def __init__(self, tools_path: str=None):
        """
        Initialize the formatter with the path to the tools JSON file.
        """
        if not tools_path:
            tools_path = AIConfig().getToolsPath() 
        self.rag_chunks = []

    def format_tools(self):
        """
        Convert the formatted tools into a list of RAG documents.
        Each document contains an ID, category, and content.
        """
        if not self.tools_path.exists():
            raise FileNotFoundError(f"Tools file not found: {self.tools_path}")
        with open(self.tools_path, "r") as f:
            tools_data = json.load(f)

        for tool_def in tools_data:
            func = tool_def["function"]
            name = func["name"]
            category = func.get("category", "General")
            description = func.get("description", "")
            examples = func.get("examples", [])
            content = f"Category: {category}\n***Tool: {name}***\n\n{description}\n\n***Examples***\n"
            if examples:
                content += "\n".join(f"\n- {example}" for example in examples) 
            else:
                content += "No examples provided."

            self.rag_chunks.append({
                "id": name,
                "category": category,
                "content": content.strip()
            })

    def to_rag_docs(self) -> list:
        return self.rag_chunks
