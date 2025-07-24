# This script parses the flattened CPN (Colored Petri Nets) fine-tuning and makes in into json.
import os, json, argparse
from pathlib import Path
from ai_iox_workflow.config import DEFAULT_AI_INSTALL_DIR
import re


def parse_flattened_cpn_to_json(text:str, out_file:Path=None, dump:bool=False) -> dict:
    cpn = {
        "places": [],
        "transitions": [],
        "arcs": []
    }

    current_section = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("***Places***"):
            current_section = "places"
            continue
        elif line.startswith("***Transitions***"):
            current_section = "transitions"
            continue
        elif line.startswith("***Arcs***"):
            current_section = "arcs"
            continue

        if current_section == "places":
            cpn["places"].append({"id": line})
        elif current_section == "transitions":
            transition = {"id": line, "conditions": [], "actions": []}
            cpn["transitions"].append(transition)
        elif current_section == "arcs":
            match = re.match(r"(\S+)\s*->\s*(\S+)(?:\s*\[(.*)\])?", line)
            if match:
                src, dst, label = match.groups()
                cpn["arcs"].append({
                    "source": src,
                    "target": dst,
                    "label": label.strip() if label else None
                })

    return cpn


# Example usage
if __name__ == "__main__":
    argparse = __import__('argparse')
    parser = argparse.ArgumentParser(description="Convert flattened CPN (Colored Petri Nets) fine-tuning data into JSON format.")
    parser.add_argument("input_file", type=str, help="Path to the samples jsonl file which includes CPN data in the assistant content. Outfile(s) - one per sample - are of the form {input_file_name}_cpn_{sample_count}.json will be used.")
    args = parser.parse_args()

    try:
        input_file = Path(args.input_file) if args.input_file else None
   #     if not input_file.is_file(): 
   #         raise ValueError(f"Input path {input_file} does not exist ....")

        print(f"Processing node: {input_file.name} ")
        with open(input_file, 'r') as f:
            full_text = f.read()
            #extract the device structure from the file
            if not full_text:
                raise ValueError(f"Warning: File {input_file} is empty. Skipping.")
            #read each line as a JSON object
            jsonl_data = []
            for line in full_text.splitlines():
                if line.strip():
                    jsonl_data.append(json.loads(line))
            if not jsonl_data:
                raise ValueError(f"Warning: No valid JSON objects found in {input_file}. Skipping.")
        sample_count = 0
        for sample in jsonl_data:
            out_file = input_file.parent / f"{input_file.stem}_cpn_{sample_count}.json"
            sample_count += 1
            if "messages" not in sample or len(sample["messages"]) < 3:
                print(f"Warning: Invalid sample format in {input_file}. Skipping.")
                continue
            # now get the first element which is role = system
            assistant_data = sample["messages"][2] if len(sample["messages"]) > 2 else None
            if not assistant_data or "content" not in assistant_data:
                print(f"Warning: No assistant content found in {input_file}. Skipping.")
                continue
            full_text = assistant_data["content"]
            if not full_text:
                print(f"Warning: Assistant content in {input_file} is empty. Skipping.")
                continue
            # find the CPN structure in the text
            # we assume the CPN structure starts with "CPN Structure:" and ends with a newline
            # if it is not found, we will skip the sample
            cpn_structure_start = full_text.find("\nCPN Structure:\n")
            if cpn_structure_start != -1:
                full_text = full_text[:cpn_structure_start]
            if not full_text:
                print(f"Warning: No CPN structure found in {input_file}. Skipping.")
                continue
            full_text = full_text.strip()
            if out_file:
                print(f"Writing to {out_file}")
            cpn_json = parse_flattened_cpn_to_json(full_text)
            if not cpn_json:
                print(f"Warning: No CPN structure found in {input_file}. Skipping.")
                continue
            print(json.dumps(cpn_json, indent=2))
            if out_file:
                with open(out_file, 'w') as out_f:
                    json.dump(cpn_json, out_f, indent=2)
                print(f"✅ Processed/wrote {out_file} from {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        raise e

