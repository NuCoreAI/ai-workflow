# deduplicates jsonl files

import json
import os   

def has_pattern(input:str, patterns:list):
    """
    Checks if the input string contains any of the specified patterns.
    :param input: The input string to check.
    :param patterns: A list of patterns to search for in the input string.
    :return: True if any pattern is found in the input, False otherwise.
    """
    for pattern in patterns:
        if pattern in input:
            return True
    return False

def deduplicate_jsonl(input_file, patterns, output_file):
    """
    Deduplicates a JSON Lines file by removing duplicate entries.
    Each line in the file should be a valid JSON object."""
    if output_file == None:
        output_file = input_file.replace('.jsonl', '_deduped.jsonl')

    seen = set()
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            line = line.strip()
            data = json.loads(line) if line else None
            if not data:
                continue
            content=data.get('messages', [])
            if len(content) < 3:
                continue
            system= content[0].get('content', '')
            if not system.startswith("You are a smart home schema assistant"):
                content[0]['content'] = "You are a smart home schema assistant."
            # Check if the third message's content is a string
            if not isinstance(content[2], dict) or 'content' not in content[2]:
                continue
            # Check if the content is a string
            if not isinstance(content[2]['content'], str):
                continue  
            user_content = content[2]['content']
            # Check if the content is empty
            if not user_content.strip():
                continue

            if has_pattern(line, patterns):
                continue

            if user_content not in seen: 
                seen.add(user_content)
                outfile.write(json.dumps({"messages": content}))
                outfile.write('\n')
                print(line)

    print(f"Deduplication complete. Output written to {output_file}")



if __name__ == "__main__":
    argparse = __import__('argparse')
    parser = argparse.ArgumentParser(description='Deduplicate JSON Lines file.')
    parser.add_argument('input_file', type=str, help='Path to the input JSON Lines file.')
    parser.add_argument('--output_file', type=str, help='Path to the output JSON Lines file.')
    parser.add_argument('--patterns', nargs='*', default=[], help='List of patterns to exclude from deduplication.')
    args = parser.parse_args()
    deduplicate_jsonl(args.input_file, args.patterns, args.output_file)


# Example usage:
# python dedupe.py input.jsonl output.jsonl --patterns "pattern1" "pattern2"