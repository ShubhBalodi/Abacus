
import asyncio
import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()

    # Load MCP server connection info
    client = MCPClient.from_config_file("mcp-server-config.json")

    # Initialize Cohere chat model
    llm = ChatCohere(
        model="command-r-plus",   # or another Cohere chat model you want
        temperature=0.3,
        max_tokens=1024,
    )

    # Create MCP Agent
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    print("\n🔹 Connected to MCP server + Cohere LLM. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        # Stream the LLM's reply
        async for chunk in agent.stream(user_input):
            print(chunk, end="", flush=True)
        print()  # newline after each response

if __name__ == "__main__":
    asyncio.run(main())
