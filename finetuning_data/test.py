OPENPIPE_API_KEY="opk_3a838d99e50c8df46b92a822938eb869ada4b8c89f"

from openpipe import OpenAI

client = OpenAI(
  openpipe={"api_key": f"{OPENPIPE_API_KEY}"}
)


while True:
    user_input = input("Enter your question: ")
    if user_input.lower() == "exit":
        break

    completion = client.chat.completions.create(
        #model="openpipe:nucore-core",
        model="openpipe:nucore-llama3",
        messages=[
            {
                "role": "system",
                "content": "You are a NuCore expert. You have been fine tuned on the NuCore schema and can answer questions about it. Now, carefully analyze the user's question and provide detailed response based on relevant NuCore data" 
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0,
        openpipe={
                "role": "system",
                "content": "You are a smart home schema assistant."
            },
    )
    print(completion.choices[0].message.content)
    if completion.choices[0].message.tool_calls:
        print("Tool calls:")
        for tool_call in completion.choices[0].message.tool_calls:
            print(f"Tool: {tool_call.name}, Arguments: {tool_call.arguments}")
    else:
        print("No tool calls made.")
    print("\n")
    print("Type 'exit' to quit or continue asking questions.")  

