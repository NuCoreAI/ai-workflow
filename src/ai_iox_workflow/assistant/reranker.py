import json,requests,re
from ai_iox_workflow.config import AIConfig
config= AIConfig()

class ToolReranker:
    def __init__(self, tools_path):
        """
            read tools and descripts from the tools.json file.
        """
        self.tools=None
        with open(tools_path, "r") as f:
            self.tools = json.load(f) 

    def is_question(self, text):
        return text.strip().endswith("?") or bool(re.match(r"^(who|what|when|where|why|how)\b", text.strip().lower()))

    def select_tool(self, query):
        payload = {
            "model": "bge-reranker",
            "query": "[QUESTION] " + query if self.is_question(query) else "[STATEMENT] " + query,
            "documents": [f"{tool['function']['name']}: {tool['function']['description']}" for tool in self.tools],
        }
        response = requests.post(config.getRerankerURL(), json=payload)

        response.raise_for_status()
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        if data:
            # Sort the 'results' list based on 'relevance_score' in descending order
            data['results'].sort(key=lambda x: x['relevance_score'], reverse=True)
            #print(json.dumps(data, indent=4))
            index = data['results'][0]['index']
            relevance_score = data['results'][0]['relevance_score']
            if relevance_score > 3.0:
                print (f"Selected tool = {self.tools[index]['function']['name']}")
            elif relevance_score < -5.0:
                print("I have no idea what you are asking, please rephrase your question.")
            else:
                print (f"Possible tool 1 {relevance_score} = {self.tools[index]['function']['name']}")
                index = data['results'][1]['index']
                relevance_score = data['results'][1]['relevance_score']
                print (f"Possible tool 2 {relevance_score} = {self.tools[index]['function']['name']}")
        

def main():
    print("Welcome to the Tool Reranker!")
    print("Type 'quit' to exit")
    reranker = ToolReranker("src/ai_iox_workflow/assistant/tools.json")

    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == 'quit':
            break

        try:
            reranker.select_tool(user_input)
        except Exception as e:
            print(f"An error occurred: {e}")
            continue 

if __name__ == "__main__":
    main()
