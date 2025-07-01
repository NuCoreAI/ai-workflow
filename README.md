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

## Workflow schema

See the [Workflow, Transition, Place, TokenType classes in models.py from llm-tap](https://github.com/advanced-stack/llm-tap/blob/main/src/llm_tap/models.py)

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


## Example queries

1. "Turn on the fan when the temperature exceeds 30°C in the office."
2. "If the electricity price is below 0.5$, start charging the car."
3. "Set the thermostat to cooling mode if the room temperature is above 75°F."
4. "Activate the siren when the door is forced open."
5. "Change the light color to blue when it's cloudy outside."
6. "Stop playing music on the AudioPlayer if Bluetooth service is disabled."
7. "Turn off the lights when the room occupancy is 'Away'."
8. "Start the fan for 10 minutes if the humidity is above 70%."
9. "Dim the lights to 50% when it's nighttime."
10. "Increase the thermostat heat setpoint by 2°C when the weather is cold."
11. "Stop charging the electric vehicle if the battery percentage reaches 80%."
12. "Enable Weather updates when it's enabled in the system."
13. "Unlock the front door when security mode is disarmed."
14. "Close the charge port if the EV battery is full."
15. "Turn off the relay if the price of electricity exceeds $1.2 per kWh."
16. "Start the audio playback on the speaker if Bluetooth is paired."
17. "Turn off all lights if any light's status is 'Off'."
18. "Activate the dehumidifier when indoor humidity exceeds 60%."
19. "If the air quality score is poor, adjust the HVAC system to improve air quality."
20. "Play a sound notification on the AudioPlayer when the door is opened."


To run the example queries and store each result in a dedicated text file, you can use the following commands:

```shell
python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Turn on the fan when the temperature exceeds 30°C in the office." > output1.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "If the electricity price is below 0.5$, start charging the car." > output2.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Set the thermostat to cooling mode if the room temperature is above 75°F." > output3.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Activate the siren when the door is forced open." > output4.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Change the light color to blue when it's cloudy outside." > output5.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Stop playing music on the AudioPlayer if Bluetooth service is disabled." > output6.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Turn off the lights when the room occupancy is 'Away'." > output7.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Start the fan for 10 minutes if the humidity is above 70%." > output8.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Dim the lights to 50% when it's nighttime." > output9.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Increase the thermostat heat setpoint by 2°C when the weather is cold." > output10.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Stop charging the electric vehicle if the battery percentage reaches 80%." > output11.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Enable Weather updates when it's enabled in the system." > output12.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Unlock the front door when security mode is disarmed." > output13.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Close the charge port if the EV battery is full." > output14.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Turn off the relay if the price of electricity exceeds $1.2 per kWh." > output15.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Start the audio playback on the speaker if Bluetooth is paired." > output16.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Turn off all lights if any light's status is 'Off'." > output17.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Activate the dehumidifier when indoor humidity exceeds 60%." > output18.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "If the air quality score is poor, adjust the HVAC system to improve air quality." > output19.txt

python3 -m ai_iox_workflow.cli \
  --profile profile.json \
  --nodes nodes.xml \
  "Play a sound notification on the AudioPlayer when the door is opened." > output20.txt
```
