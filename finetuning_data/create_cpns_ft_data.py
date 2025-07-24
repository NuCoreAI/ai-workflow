## Generate OpenPipe fine-tuning data for NuCore smart home devices Colored Petri Nets(CPN) format
from openai import OpenAI
import json
import os
from pathlib import Path
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


#MODEL = "gpt-4o"  # Use the latest model available
MODEL = "gpt-4.1-mini"
TEMPERATURE = 0.3
MAX_TOKENS = 32_000 # Adjust based on your needs, but ensure it fits within the model's limits

SYSTEM_PROMPT = """
You are an expert in smart home automation and Colored Petri Nets (CPNs) specializing in NuCore technology. I will provide you with flattened structured descriptions of smart devices, including their properties, commands: both sends and accepts, parameters, and units of measure.

Your task is to generate **OpenPipe fine-tuning samples** that teach a model to construct Colored Petri Nets (CPNs) for smart home automation routines. 

Output for each sample must include:
    1. System prompt: "You are a smart home assistant and NuCore expert and you are able to generate CPNs for smart home automation and optimization routines"
    2. User prompt: includes device structure explicitly (labelled "DEVICE STRUCTURE:") followed by a realistic user automation or optimization query or request"
    3. Assistant reply: include clear, step-by-step reasoning based on device context and user query, followed by the result or direct answer last (reasoning should come before any conclusions or lists; reverse this order if the user's examples initially show results before rationale).


Output format for each sample: a single JSON object per line as per OpenPipe standards as follows:
{
  "messages": [
    {"role": "system", "content": "You are a smart home assistant and NuCore expert."},
    {"role": "user", "content": "DEVICE STRUCTURE:\n<device_info>\n\nUSER QUERY:\n<query here>"},
    {"role": "assistant", "content": "<correct, context-aware, reasoned response with flattened and well structured CPN structure and logic>"}
  ]
}

Each example should include:
- A user query that describes the automation goal.
- The query must avoid using explicit device names or commands, focusing instead on general automation and optimization principles, desired changes in properties, locations, idevice states, or outcomes.
-- For example:
--- "Set the cool set point for Ecobee thermostat" should be rephrased as "Adjust the temperature in the living room to a comfortable level."
--- "Charge my electric car" should be rephrased as "Ensure my car is charged to a sufficient level."
--- "If the value of price in the device is less than 10, then optimize the device for cost savings" should be rephrased as "Optimize the device for cost savings when the price is below a certain threshold."
--- "Set the living room thermostat to 22 degrees" should be rephrased as "Adjust the temperature in the living room to a comfortable level."
- An assistant response with a flattened and well-structured CPN.
- The CPN must use places, transitions, and tokens with color (data).
- Use actual properties and commands from the devices.
- Include a variety of samples:
  - Simple logic: one condition, one action.
  - Medium logic: if/else or multi-condition.
  - Complex logic: nested conditions, multiple devices, command parameters, time-triggered logic.
  - Time triggered logic should include
  -- Sunrise/sunset events
  -- From/to times
  -- Days of the week, months of the year, holidays, etc.

- Structure: Strictly follow the output format above, always using double quotes for all JSON.
- Length: Assistant responses should be thorough, including both detailed reasoning steps and a clear, concise conclusion/answer.

Use different devices for different examples. Use realistic values for properties (e.g., temperatures, prices, states).

Generate 10 varied examples spanning multiple devices and automation scenarios. Ensure each example is unique and covers different aspects of smart home automation.

"""

def generate_openpipe_entries(full_text, output_path, dump=True):


    client = OpenAI(api_key=OPENAI_API_KEY)  # or use environment variable
    jsonl_data = [] 

    # replace <device_info> in the system prompt with the actual device info
    system_prompt = SYSTEM_PROMPT.replace("<device_info>", full_text)

    if full_text: 
        try:
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )

            assistant_reply = response.choices[0].message.content.strip()
            if not assistant_reply:
                ("Assistant reply is empty. Please check the input text.")
            # Split the assistant reply into individual JSON objects
            entries = assistant_reply.split("\n")
            for entry in entries:
                entry = entry.strip()
                if entry:
                    try:
                        json_data = json.loads(entry)
                        jsonl_data.append(json_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e} | Entry: {entry}")

        except Exception as e:
            print(f"Error: {e} | Input: {full_text[:60]}")

    with open(output_path, "w") as f:
        for item in jsonl_data:
            f.write(json.dumps(item) + "\n")

    print(f"✅ {len(jsonl_data)} entries saved to {output_path}")

# Example usage
if __name__ == "__main__":
    argparse = __import__('argparse')
    parser = argparse.ArgumentParser(description="Generate OpenPipe fine-tuning entries from device descriptions.")
    parser.add_argument("--input_path", type=str, help="Path to the directory that holds profiles and nodes directories within. If none given, it will use the default references directory.")
    parser.add_argument("--output_path", type=str, help="Path to the output directory where flattened structures are stored. If none given, it will be printed to stdout.")
    args = parser.parse_args()

    INPUT_DIR = Path(os.path.join(os.path.expanduser("~"), DEFAULT_AI_INSTALL_DIR, "finetuning_data", "datasets", "devices"))
    OUTPUT_DIR = Path(os.path.join(os.path.expanduser("~"), DEFAULT_AI_INSTALL_DIR, "finetuning_data", "datasets", "cpns"))

    input_path = Path(args.input_path) if args.input_path else INPUT_DIR
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"Input path {input_path} does not exist or is not a directory.")

    output_path = Path(args.output_path) if args.output_path else OUTPUT_DIR

    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"Input path {input_path} does not exist or is not a directory.")

    if not output_path.exists() or not output_path.is_dir():
        raise ValueError(f"Output path {output_path} does not exist or is not a directory.")

    # now traverse the input directory where you will find profiles and nodes directories
    # start with files in the nodes directory and then use the name of the file (without extension) to find the corresponding profile in the profiles directory
    for node_file in INPUT_DIR.glob("*.jsonl"):
        
        try:
            print(f"Processing node: {node_file.name} ")
            with open(node_file, 'r') as f:
                full_text = f.read()
                #extract the device structure from the file
                if not full_text:
                    print(f"Warning: File {node_file} is empty. Skipping.")
                    continue
                #read each line as a JSON object
                jsonl_data = []
                for line in full_text.splitlines():
                    if line.strip():
                        jsonl_data.append(json.loads(line))
                if not jsonl_data:
                    print(f"Warning: No valid JSON objects found in {node_file}. Skipping.")
                    continue
                sample_count = 0
                out_file = output_path / f"{node_file.stem}_{sample_count}.jsonl"
                full_text = ""
                for sample in jsonl_data:
                    if "messages" not in sample or len(sample["messages"]) < 3:
                        print(f"Warning: Invalid sample format in {node_file}. Skipping.")
                        continue
                    # now get the first element which is role = system
                    user_data = sample["messages"][1] if len(sample["messages"]) > 1 else None
                    if not user_data or "content" not in user_data:
                        print(f"Warning: No user content found in {node_file}. Skipping.")
                        continue
                    content = user_data["content"]
                    if not content:
                        print(f"Warning: User content in {node_file} is empty. Skipping.")
                        continue
                    # now remove the DEVICE STRUCTURE: part
                    device_structure_start = content.find("DEVICE STRUCTURE:")
                    if device_structure_start != -1:
                        content = content[device_structure_start + len("DEVICE STRUCTURE:"):].strip()
                    if not content:
                        print(f"Warning: No device structure found in {node_file}. Skipping.")
                        continue
                    # now remove all the extra text starting with \nUSER QUERY:\n and all the way to the end of the string
                    user_query_start = content.find("\nUSER QUERY:\n")
                    if user_query_start != -1:
                        content = content[:user_query_start]
                    if not content:
                        print(f"Warning: No device structure found in {node_file}. Skipping.")
                        continue
                    content = content.strip()
                    full_text += content + "\n"
            if out_file:
                print(f"Writing to {out_file}")
                generate_openpipe_entries(full_text, out_file, dump=True)

        except Exception as e:
            print(f"Error processing device documents for node {node_file}. Skipping: {e}")
            continue    
                    
                    
                    
     #EXAMPLES.append((node_data, profile_data))

#    generate_openpipe_entries(EXAMPLES, "openpipe_finetune.jsonl")
