# AI Workflow

## Goal

This library goal is to convert a user query written in natural language to programs for IoX systems.

## Quick start

Installation:

```shell
git clone https://github.com/NuCoreAI/ai-workflow.git
cd ai-workflow
make setup
```

Now, you need 2 models using the GGUF format (llama.cpp):

- A large language model (for instance llama-3.1-8b you can find [here](https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF))
- A re-ranker model (for instance bge-reranker-v2-m3 you can find [here](https://huggingface.co/gpustack/bge-reranker-v2-m3-GGUF))


For the next part you need:

- a IoX profile using the JSON format
- a XML export of the IoX nodes

```python
python3 -m ai_iox_workflow.cli \
  --workflow-llm-model llama-3.1-8b \
  --profile profile.json \
  --nodes nodes.xml \
  "If the electricity price is above 0.4$, stop charging the car"
```

Example response:

```plain
Identifying relevant nodes...
Found:
- sensor: Utility Signals (oadr3) [Electricity price]
- sensor: Charging Info [Estimated Range]
- sensor: Charging Info [Charge energy added]
- sensor: Charging Info [Charger voltage]
- sensor: Charging Info [Last Command Status]
- sensor: Charging Info [Charging Requested]
- sensor: Charging Info [Charging Power]
- command: Charging Info [Charging Control]
- command: Charging Info [Set Max Charge Current]
- command: Charging Info [Charge Port Control]
Building workflow...
================================================================================
Workflow Details:
Transition:
  Guard:
    Conditions: AND
      - Utility Signals (oadr3) [Electricity price] GREATER THAN ITokenValue(value=0.4)
  Output:
    Set Charging Info [Charging Control] to Stop
================================================================================
JSON Representation
{
  "transition": {
    "inputs": [
      {
        "place": "sensor: Utility Signals (oadr3) [Electricity price]"
      }
    ],
    "guard": {
      "conditions": [
        {
          "place_state": {
            "place": "Utility Signals (oadr3) [Electricity price]",
            "operator": "GREATER THAN",
            "value": {
              "value": 0.4
            }
          }
        }
      ],
      "conditions_operator": "AND"
    },
    "output": {
      "place": "command: Charging Info [Charging Control]",
      "token_produced": {
        "set_value": "Charging Info [Charging Control]",
        "to": {
          "value": "Stop"
        }
      }
    }
  }
}
```

## Workflow structure

See [Workflow class in models.py from llm-tap](https://github.com/advanced-stack/llm-tap/blob/main/src/llm_tap/models.py)

## CLI

```shell
python3 -m ai_iox_workflow.cli -h

usage: cli.py [-h] --profile PROFILE --nodes NODES [--workflow-llm-model WORKFLOW_LLM_MODEL]
              [--reranker-model RERANKER_MODEL]
              query

Generate an AI workflow based on a query.

positional arguments:
  query                 The query to generate the workflow from.

options:
  -h, --help            show this help message and exit
  --profile PROFILE     Path to the profile JSON file.
  --nodes NODES         Path to the nodes XML file.
  --workflow-llm-model WORKFLOW_LLM_MODEL
                        Accepts any GGUF LLM models
  --reranker-model RERANKER_MODEL
                        Accepts GGUF re-ranking models. Qwen3 reranking is *not* yet supported by llama.cpp.
```
