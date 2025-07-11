import json,requests
API_URL = "http://localhost:8000/v1/rerank"


class ToolReranker:
    def __init__(self, tools_path):
        """
            read tools and descripts from the tools.json file.
        """
        self.tools=None
        with open(tools_path, "r") as f:
            self.tools = json.load(f) 

    def select_tool(self, query):
        payload = {
            "model": "bge-reranker",
            "query": query,
            "documents": [f"{tool['function']['name']}: {tool['function']['description']}" for tool in self.tools],
        }
        response = requests.post(API_URL, json=payload)

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
            print (f"Selected tool = {self.tools[index]['function']['name']}")
            index = data['results'][1]['index']
            print (f"Selected tool = {self.tools[index]['function']['name']}")
        

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
