import re

import requests
import json
import asyncio, argparse
from ai_iox_workflow.iox.nucore_api import nucoreAPI
from ai_iox_workflow.iox.nucore_programs import nucorePrograms
from ai_iox_workflow.config import AIConfig
from ai_iox_workflow.nucore import NuCore


config = AIConfig()

# Local llama.cpp server
API_URL = "http://localhost:8000/v1/chat/completions"

with open("src/ai_iox_workflow/assistant/system.prompt.qwen", "r") as f:
    system_prompt = f.read().strip()

with open(config.getToolsFile()) as f:
    tools = json.load(f)
    for tool in tools:
        if "function" in tool and "examples" in tool["function"]:
            del tool["function"]["examples"]

 
comfort_settings="""
     Normal: for price between 30 cents and 49 cents
     Moderate: for price between 50 cents and 79 cents 
     High: for price above 80 cents""" 


class NuCoreAssistant:
    def __init__(self, args, websocket=None):
        self.websocket=websocket
        self.sent_system_prompt=False
        if not args:
            raise ValueError("Arguments are required to initialize NuCoreAssistant")
        self.nuCore = NuCore(
            profile_path=args.profile_path,
            nodes_path=args.nodes_path,
            url=args.url,
            username=args.username,
            password=args.password
        )
        self.nuCore.load()

    async def utility_price_available_routine(self, customer_input:str):
        await self.send_response("Yes, you have an OpenADR 3.0 VEN service that offers both price and GHG signals!", True)
  
    async def which_device_automatable(self, customer_input:str):
        await self.send_response("I can optimize and automate your Batmobile, your Ecobee - Thermostat, Family Room Hue, Living Room Hue, and Matter Switch. Unfortunately, I cannot do anything with your Bluetooth Service.", True)

    async def get_comfort_settings(self, customer_input:str):
        await self.send_response(f"Your comfort settings are: \r\n{comfort_settings}", True)

    async def set_comfort_settings(self, customer_input:str):
        await self.send_response(f"Ok, I set your comfort settings to: \r\n{customer_input['customer_input']}", True)
    
    async def general_nucore_info(self, customer_input:str):
        await self.send_response(f"Ok, I'll give you some high level information about NuCore.AI and how it works", True) 

    async def pass_to_system(self, customer_input:str):
        await self.send_response(f"I have no clue what you're talking about ... please rephrase your request", True) 

    async def create_automation_routine(self,customer_input:list):
        if not customer_input or 'individual_prompts' not in customer_input :
            return ("apologies, it seems that I may have lost your request. Please try again")
        individual_prompts=customer_input['individual_prompts']
        if len (individual_prompts) == 0:
            return ("apologies, I couldn't understand your prompt.")

        ep = nucoreAPI()
        all_programs=nucorePrograms()
        available_nodes=ep.get_nodes()
        runtime_profile=ep.get_profiles()

        for individual_prompt in individual_prompts:
            await self.send_response(f"Ok, now: {individual_prompt}")
            #user_prompt=self.get_auto_routine_prompt(individual_prompt, available_nodes, runtime_profile)
            #system_prompt=self.get_system_prompt()

        return ep.upload_programs(all_programs)


    async def process_tool_call(self,tool_name:str, tool_args):
        print (f"Tool call: {tool_name} with arguments: {tool_args if tool_args else 'None'}")
        if not tool_name:
            return None
        
        if tool_name == "create_automation_routine":
            return await self.create_automation_routine(tool_args)
        elif tool_name == "utility_price_available_routine":
            return await self.utility_price_available_routine(tool_args)
        elif tool_name == "which_device_automatable":
            return await self.which_device_automatable(tool_args)
        elif tool_name == "general_nucore_info":
            return await self.general_nucore_info(tool_args)
        elif tool_name == "get_comfort_settings":
            return await self.get_comfort_settings(tool_args)
        elif tool_name == "set_comfort_settings":
            return await self.set_comfort_settings(tool_args)
        elif tool_name == "pass_to_system":
            return await self.pass_to_system(tool_args)
        return await self.send_response("Ooops, couldn't find the tool to process your request ... ")

    async def send_response(self, message, is_end=False):
        if self.websocket:
            await self.websocket.send_json({
                "sender": "bot",
                "message": message,
                "end": 'true' if is_end else 'false'
            })
        else:
            print(f"Assistant: {message}")

    async def process_customer_input(self, query:str, num_rag_results=5, rerank=True):
        """
        Process the customer input by sending it to the AI model and handling the response.
        :param query: The customer input to process.
        :param num_rag_results: The number of RAG results to use for the actual query
        :param rerank: Whether to rerank the results.
        """

        if not query:
            print("No query provided, exiting ...")
        messages =[]
        system_messages = []
        
        system_messages.append({
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt 
                    }
                ]
        })

        #first use rag for relevant documents
        rag_results = self.nuCore.query(query, num_rag_results, rerank)
        if rag_results:
            for document in rag_results['documents']:
                system_messages.append({
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Relevant document: {document}"
                        }
                    ]
                })

        user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query 
                    }
                ]
        }

        if rag_results:
            print(f"\n\n*********************Top 5 Query Results:(Rerank = {rerank})********************\n\n")
            for i in range(len(rag_results['ids'])):
                print(f"{i+1}. {rag_results['ids'][i]} - {rag_results['distances'][i]} - {rag_results['relevance_scores'][i]}")
            print("\n\n***************************************************************\n\n")

    #    if not self.sent_system_prompt:
    #        messages.append(system_messages)
    #        self.sent_system_prompt = True

        messages.append(user_message)
        # Step 1: Get tool call
        response = requests.post(API_URL, json={
            "messages": messages,
            "tools": tools, 
            "max_tokens": 128_000,
            "temperature": 0.2,
            "tool_choice": "auto"
        })

        response.raise_for_status()
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            print("No choices returned in the response.")
            return None

        # Extract tool call
        tool_calls = data["choices"][0]["message"].get("tool_calls", [])
        if not tool_calls:
            print("No tool call returned.")
            print(data["choices"][0]["message"])
            return None

        tool_call = tool_calls[0]
        tool_name = tool_call["function"]["name"]
        tool_args = None
        if tool_call["function"]["arguments"]:
            tool_args = json.loads(tool_call["function"]["arguments"])
        await self.process_tool_call(tool_name, tool_args)

        return None 
    

async def main(args):
    print("Welcome to NuCore AI Assistant!")
    print("Type 'quit' to exit")
    assistant = NuCoreAssistant(args, websocket=None)  # Replace with actual websocket connection if needed
    
    while True:
        try:
            user_input = input("\nEnter your request: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
                
            if not user_input:
                print("Please enter a valid request")
                continue
                
            await assistant.process_customer_input(user_input)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Loader for NuCore Profile and Nodes XML files."
    )
    parser.add_argument(
        "--profile",
        dest="profile_path",
        type=str,
        required=False,
        help="Path to the profile JSON file (profile-xxx.json)",
    )
    parser.add_argument(
        "--nodes",
        dest="nodes_path",
        type=str,
        required=False,
        help="Path to the nodes XML file (nodes.xml)",
    )
    parser.add_argument(
        "--url",
        dest="url",
        type=str,
        required=False,
        help="The URL to fetch nodes and profiles from the nucore platform",
    )
    parser.add_argument(
        "--username",
        dest="username",
        type=str,
        required=False,
        help="The username to authenticate with the nucore platform",
    )
    parser.add_argument(
        "--password",
        dest="password",
        type=str,
        required=False,
        help="The password to authenticate with the nucore platform",
    )

    args = parser.parse_args()
    asyncio.run(main(args))

    