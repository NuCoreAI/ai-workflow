import re

import requests
import json
import httpx
import asyncio, argparse

from sympy import true
from ai_iox_workflow.iox.nucore_api import nucoreAPI
from ai_iox_workflow.iox.nucore_programs import nucorePrograms
from ai_iox_workflow.config import AIConfig
from ai_iox_workflow.nucore import NuCore

"""
Best option
build.cuda/bin/llama-server -m /home/michel/workspace/nucore/models/finetuned/qwen2.5-coder-dls-7b/qwen2.5-coder-dls-7b-Q4_K_M.gguf --jinja --host localhost -c 60000 --port 8013 -t 15  --n-gpu-layers 32 --batch-size 8192
"""
tools = False

config = AIConfig()
# if tools else "/system.prompt.qwen2.5"}", "r") as f:
with open(f"{config.__assistant_path__}/system.prompt.qwen2.5-tools", "r") as f:
    system_prompt = f.read().strip()

if tools:
    with open(config.getToolsFile()) as f:
        tools = json.load(f)
        #for tool in tools:
        #    if "function" in tool and "examples" in tool["function"]:
        #        del tool["function"]["examples"]

 
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


    async def get_comfort_settings(self, customer_input:str):
        await self.send_response(f"Your comfort settings are: \r\n{comfort_settings}", True)

    async def set_comfort_settings(self, customer_input:str):
        await self.send_response(f"Ok, I set your comfort settings to: \r\n{customer_input['customer_input']}", True)
    
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
    
    async def process_property_query(self, prop_query:list):
        if not prop_query or len(prop_query) == 0:
            return "No property query provided"
        for property in prop_query:
            # Process the property query
            device_id = property.get('device_id')
            if not device_id:
                print(f"No device ID provided for property query: {property}")
                continue
            properties = await self.nuCore.get_properties(device_id)
            if not properties:
                print(f"No properties found for device {property['device_id']}")
                continue
            prop_id = property.get('property_id')
            prop_name = property.get('property_name')
            if prop_id:
                prop = properties.get(prop_id)
                if prop:
                    text = f"\nNuCore: {prop_name if prop_name else prop_id} value for device {property['device_id']} is: {prop.formatted if prop.formatted else prop.value}"
                    #await self.send_user_content_to_llm(text)
                    await self.send_response(text, True)
                else:
                    print( f"Property {prop_id} not found for device {property['device_id']}")
            else:
                print(f"No property ID provided for device {property['device_id']}")


    async def process_tool_call(self,full_response:str, begin_marker, end_marker):
        if not full_response or not begin_marker or not end_marker:
            return None
        
        parameters = []
        command_pattern = re.compile(rf'{begin_marker}(.*?){end_marker}', re.DOTALL)
        matches = command_pattern.findall(full_response)

        for match in matches:
            try:
                # Remove any comments that start with //, # or /* and end with */
                match = re.sub(r'//.*?$|#.*?$|/\*.*?\*/', '', match, flags=re.MULTILINE)
                # Remove any leading or trailing whitespace
                match = match.strip()
                if not match:
                    continue
                # Parse the JSON block
                parameter_json = json.loads(match.strip())
                parameters.append(parameter_json)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from nucore block: {e}")
                return None
            
        if len(parameters) > 0:
            if begin_marker == "__BEGIN_NUCORE_COMMAND__":
                return await self.nuCore.send_commands(parameters)
        
            elif begin_marker == "__BEGIN_NUCORE_PROPERTY_QUERY__":
                return await self.process_property_query(parameters) 
        
        return None

    async def send_response(self, message, is_end=False):
        if not message:
            return
        if self.websocket:
            await self.websocket.send_json({
                "sender": "bot",
                "message": message,
                "end": 'true' if is_end else 'false'
            })
        else:
            print(message, end="", flush=True)

    async def send_user_content_to_llm(self, user_content):
        """
        Send user content to the LLM for processing.
        :param user_content: The content provided by the user.
        """
        if not user_content:
            print("No user content provided, exiting ...")
            return
        user_message = {
            "role": "user",
            "content": f"{user_content.strip()}"
        }
        messages = [user_message]
        payload={
            "messages": messages,
            "stream": False,
            "temperature": 2.0,
            "max_tokens": 60_000,
        }

        response = requests.post(config.getModelURL(), json=payload)
        response.raise_for_status()
        await self.send_response(response.json()["choices"][0]["message"]["content"])
        return None

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

        device_docs = ""
        if not self.nuCore.load_devices(include_profiles=False):
                raise ValueError("Failed to load devices from NuCore. Please check your configuration.")

        # Load RAG documents
        #if not self.nuCore.load_rag_docs(dump=False):
        #    raise ValueError("Failed to load RAG documents from NuCore. Please check your configuration.")
        rag = self.nuCore.format_nodes()
        if not rag:
            raise ValueError(f"Warning: No RAG documents found for node {self.nuCore.url}. Skipping.")

        rag_docs = rag["documents"]
        if not rag_docs:
            raise ValueError(f"Warning: No documents found in RAG for node {self.nuCore.url}. Skipping.")

        for rag_doc in rag_docs:
            device_docs += "\n" + rag_doc

        sprompt = system_prompt.replace("{device_docs}", device_docs)
        sprompt.strip()
        print(sprompt)

        system_message = {
            "role": "system",
            "content": sprompt
        }
        user_message = {
            "role": "user",
            "content": f"USER QUERY:\n{query.strip()}"
        }

        #first use rag for relevant documents
        #rag_results = self.nuCore.query(query, num_rag_results, rerank)
        #context = None
        #if rag_results:
        #    context = "***Relevant documents***\n"
        #    for document in rag_results['documents']:
        #        context += f"---\n{document}"
#
#        query = query.strip() if not context else f"{context.strip()}\n\n Customer Question: {query.strip()}"

#        print (f"\n\n*********************Customer Query: {query}********************\n\n")

#        if rag_results:
#            print(f"\n\n*********************Top 5 Query Results:(Rerank = {rerank})********************\n\n")
#            for i in range(len(rag_results['ids'])):
#                print(f"{i+1}. {rag_results['ids'][i]} - {rag_results['distances'][i]} - {rag_results['relevance_scores'][i]}")
#            print("\n\n***************************************************************\n\n")

        #if not self.sent_system_prompt:
        messages.append(system_message)
        self.sent_system_prompt = True

        messages.append(user_message)
        # Step 1: Get tool call
        payload={
            "messages": messages,
            "stream": True,
            'cache_prompt':True,
            "n_keep": -1,
            "temperature": 0.0,
            "max_tokens": 60_000,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto" 
        full_response = ""
        try:
            with httpx.stream("POST", config.getModelURL(), timeout=100, json=payload
            ) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        token_data = line[len(b"data: "):]
                        try:
                            finish_reason = json.loads(token_data.strip())['choices'][0]['finish_reason']
                            if finish_reason == "stop":
                                break
                            token_data = json.loads(token_data.strip())['choices'][0]['delta'].get('content', '')
                        except json.JSONDecodeError:
                            continue
                        if token_data:
                            # Print the token data as it arrives
                            if isinstance(token_data, bytes):
                                token_data = token_data.decode("utf-8")
                            await self.send_response(token_data, False)
                            #full_response += token_data  # Collect the token data
                            full_response += token_data


            # now parse the full response and look for blocks between __NUCORE_COMMAND_BEGIN__ and __NUCORE_COMMAND_END__. 
            # convert the blocks to json and add to list
            await self.process_tool_call(full_response, "__BEGIN_NUCORE_COMMAND__", "__END_NUCORE_COMMAND__")
            await self.process_tool_call(full_response, "__BEGIN_NUCORE_PROPERTY_QUERY__", "__END_NUCORE_PROPERTY_QUERY__")

        except Exception as e:
            print(f"An error occurred while processing the customer input: {e}")
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
                
            await assistant.process_customer_input(user_input, num_rag_results=3, rerank=False)
            
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

    