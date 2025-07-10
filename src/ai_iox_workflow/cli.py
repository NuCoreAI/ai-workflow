import json
import argparse
from dataclasses import asdict
from time import time
from builder import Builder
from config import AIConfig


def main(profile:str, nodes:str, llm_model:str, reranker_model:str, query:str, output_work_flow:str=None):

    builder = Builder.from_file(
        profile,
        nodes
    )

    builder.workflow_llm_model = llm_model 
    builder.reranker_model = reranker_model 

    start_time = time()
    workflow = builder.generate_workflow(args.query)
    elapsed_time = time() - start_time

    print("=" * 80)
    print(f"Original Query: {args.query}")
    print(workflow)
    print("=" * 80)
    print("JSON Representation")
    workflow_data = json.dumps(asdict(workflow), indent=2)
    print(workflow_data)
    if args.output_workflow:
        with open(args.output_workflow, "w") as file:
            file.write(workflow_data)

    print("=" * 80)
    print(f"Elapsed Time: {elapsed_time:.2f} seconds")


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

    parser.add_argument(
        "--profile",
        type=str,
        help="Path to the profile JSON file."
    )

    parser.add_argument(
        "--nodes", 
        type=str, 
        help="Path to the nodes XML file."
    )

    parser.add_argument(
        "--workflow-llm-model",
        type=str,
        help="Accepts any GGUF LLM models",
    )

    parser.add_argument(
        "--reranker-model",
        type=str,
        help="Accepts GGUF re-ranking models. Qwen3 reranking is *not* yet supported by llama.cpp.",
    )

    parser.add_argument(
        "--output-workflow",
        type=str,
        help="Write generated workflow json file",
    )

    #the actual query
    parser.add_argument(
        "--query", 
        type=str,
        help="The query to generate the workflow from.",
    )

    args = parser.parse_args()
    query = args.query
    if not query:
        query = input("what's your query?") 

    config=AIConfig(args.data_path, args.model_path)
    import os
    print(os.getcwd())

    main(
        profile=config.getProfile(args.profile),
        nodes=config.getNodes(args.nodes),
        llm_model=config.getLLMModel(args.workflow_llm_model),
        reranker_model=config.getRerankerModel(args.reranker_model),
        query=query,
        output_work_flow=args.output_workflow
    )
