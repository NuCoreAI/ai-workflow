from openpipe import OpenAI
import json
import argparse
from pathlib import Path
import os



from ai_iox_workflow.config import DEFAULT_AI_INSTALL_DIR
from ai_iox_workflow.nucore import NuCore


# === CONFIGURATION ===
SECRETS_DIR = Path(os.path.join(os.path.expanduser("~"), DEFAULT_AI_INSTALL_DIR, "finetuning_data", "secrets"))
if not SECRETS_DIR.exists():
    raise FileNotFoundError(f"Secrets directory {SECRETS_DIR} does not exist. Please create it and add your OpenAI API key.")
# Load the OpenAI API key from the secrets file
if not (SECRETS_DIR / "keys.py").exists():
    raise FileNotFoundError(f"Secrets file {SECRETS_DIR / 'keys.py'} does not exist. Please create it and add your OpenAI API key.")
exec(open(SECRETS_DIR / "keys.py").read())  # This will set OPENAI_API_KEY  



client = OpenAI(
  openpipe={"api_key": f"{OPENPIPE_API_KEY}"}
)

nuCore = NuCore(
    url="http://192.168.4.225:8080",
    username="admin",
    password="admin",
)

device_docs = ""
try:
    nuCore.load(include_rag_docs=False)
    rag = nuCore.format_nodes()
    if not rag:
        raise ValueError(f"Warning: No RAG documents found for node {nuCore.url}. Skipping.")

    rag_docs = rag["documents"]
    if not rag_docs:
        raise ValueError(f"Warning: No documents found in RAG for node {nuCore.url}. Skipping.")

    for rag_doc in rag_docs:
        device_docs += rag_doc

except Exception as e:
    raise ValueError(f"Error processing RAG documents for node {nuCore.url}. Skipping: {e}")

system_prompt = f"""You are a smart home assistant and NuCore expert.

You will receive a DEVICE STRUCTURE followed by a USER QUERY.

Use the DEVICE STRUCTURE to understand the device’s properties, accepted and sent commands, and parameters (including range, unit, and type).

Your task:
- If the query is informational, respond clearly using context from the DEVICE STRUCTURE.
- If the query requires automation or optimization, generate a Colored Petri Net (CPN) that models the goal.

The CPN should:
- Include **places**, **transitions**, and **tokens** with color (data).
- Represent triggers, conditions, actions, and data flow accurately.
- Be structured, readable, and useful for conversion to other automation formats.

DEVICE STRUCTURE:
{device_docs}
"""


while True:

    user_input = input("Your request: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

    completion = client.chat.completions.create(
        model="openpipe:nucore-gemma", #<-- this is llama 3.1 8b
        #model="openpipe:nucore-gemma-3-4b",
        messages=[
            {
                "role": "system",
                "content": system_prompt 
            },
            {
                "role": "user",
                "content": "USER QUERY:\n" + user_input
            }
        ],
        temperature=0,
        openpipe={
            "tags": {
                "prompt_id": "counting",
                "any_key": "any_value"
            }
        },
    )

    print("\nResponse:\n", completion.choices[0].message.content.strip())
