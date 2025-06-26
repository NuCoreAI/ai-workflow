import json
import argparse
from dataclasses import asdict

from ai_iox_workflow.builder import Builder


def main():
    parser = argparse.ArgumentParser(
        description="Generate an AI workflow based on a query."
    )
    parser.add_argument(
        "query", type=str, help="The query to generate the workflow from."
    )
    parser.add_argument(
        "--profile",
        type=str,
        required=True,
        help="Path to the profile JSON file.",
    )
    parser.add_argument(
        "--nodes", type=str, required=True, help="Path to the nodes XML file."
    )
    parser.add_argument(
        "--workflow-llm-model",
        type=str,
        default="qwen3-1.7b",
        help="Accepts any GGUF LLM models",
    )
    parser.add_argument(
        "--reranker-model",
        type=str,
        default="bge-reranker-v2-m3",
        help="Accepts GGUF re-ranking models. Qwen3 reranking is *not* yet supported by llama.cpp.",
    )

    args = parser.parse_args()

    builder = Builder.from_file(
        args.profile,
        args.nodes,
    )

    builder.workflow_llm_model = args.workflow_llm_model
    builder.reranker_model = args.reranker_model

    workflow = builder.generate_workflow(args.query)

    print("=" * 80)
    print(workflow)
    print("=" * 80)
    print("JSON Representation")
    print(json.dumps(asdict(workflow), indent=2))


if __name__ == "__main__":
    main()
