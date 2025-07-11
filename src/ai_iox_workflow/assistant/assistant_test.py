from llama_cpp import Llama
import time
import argparse
import os
from ai_iox_workflow.config import AIConfig

def stream_chat_with_stats(prompt, model_path, max_tokens=100_000, num_threads=16):
    llm = Llama(model_path=model_path, n_threads=num_threads)
    stream = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True,
    )
    token_count = 0
    for chunk in stream:
        content = chunk['choices'][0]['delta'].get('content', '')
        if content:
            print(content, end='', flush=True)
            # Count tokens by splitting on whitespace (approximation)
            token_count += len(content.split())
    return token_count

def stream_chat(prompt, model_path, max_tokens=128):
    llm = Llama(model_path=model_path)
    stream = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        content = chunk['choices'][0]['delta'].get('content', '')
        if content:
            print(content, end='', flush=True)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate an AI workflow based on a query."
    )

    parser.add_argument(
        "--data-path", 
        type=str,
        help="The where we can find data such as nodes and profiles.",
    )

    parser.add_argument(
        "--model-path", 
        type=str,
        help="The where we can find the models for reranker and the llm.",
    )

    config=AIConfig(
        data_path=parser.parse_args().data_path,
        models_path=parser.parse_args().model_path
    )
    print(os.getcwd())

    prompt = input("what's your query?")

    start_time = time.time()

    token_count = stream_chat_with_stats(prompt, config.getLLMModel(), max_tokens=8_000)

    elapsed = time.time() - start_time
    print(f"\n\nTotal tokens: {token_count}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    if elapsed > 0:
        print(f"Tokens per second: {token_count / elapsed:.2f}")

