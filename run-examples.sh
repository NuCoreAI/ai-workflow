queries=(
    "Turn on the fan when the temperature exceeds 30°C in the office."
    "If the electricity price is below 0.5$, start charging the car."
    "Set the thermostat to cooling mode if the room temperature is above 75°F."
    "Activate the siren when the door is forced open."
    "Change the light color to blue when it's cloudy outside."
    "Stop playing music on the AudioPlayer if Bluetooth service is disabled."
    "Turn off the lights when the room occupancy is 'Away'."
    "Start the fan for 10 minutes if the humidity is above 70%."
    "Dim the lights to 50% when it's nighttime."
    "Increase the thermostat heat setpoint by 2°C when the weather is cold."
    "Stop charging the electric vehicle if the battery percentage reaches 80%."
    "Enable Weather updates when it's enabled in the system."
    "Unlock the front door when security mode is disarmed."
    "Close the charge port if the EV battery is full."
    "Turn off the relay if the price of electricity exceeds $1.2 per kWh."
    "Start the audio playback on the speaker if Bluetooth is paired."
    "Turn off all lights if any light's status is 'Off'."
    "Activate the dehumidifier when indoor humidity exceeds 60%."
    "If the air quality score is poor, adjust the HVAC system to improve air quality."
    "Play a sound notification on the AudioPlayer when the door is opened."
)

for i in "${!queries[@]}"; do
    query="${queries[$i]}"
    # Replace spaces with underscores for the filename
    output_file="examples/llama-3.1-8b-output-${i}.txt"

    # Run the Python script and save the output to the file
    python3 -m ai_iox_workflow.cli \
        --workflow-llm-model llama-3.1-8b \
        --profile profile.json \
        --nodes nodes.xml \
        "$query" \
    > "$output_file"
done
