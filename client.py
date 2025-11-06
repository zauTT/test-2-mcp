#!/usr/bin/env python3
"""
Weather MCP Client
==================
Terminal client for asking weather questions.
This connects to the MCP server and uses Claude to interpret natural language queries.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

# Initialize Anthropic client
# Note: This requires ANTHROPIC_API_KEY environment variable
anthropic = Anthropic()


async def run_weather_query(query: str):
    """
    Process a weather query using the MCP server and Claude.
    
    Args:
        query: Natural language weather question from the user
    """
    # Get the path to the server script
    server_script = Path(__file__).parent / "server.py"
    
    # Set up server parameters - we'll run the Python server script
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None  # Inherits current environment (including API keys)
    )
    
    print(f"\n🔍 Processing query: {query}")
    print("📡 Connecting to weather server...\n")
    
    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"✅ Connected! Available tools: {[tool.name for tool in tools.tools]}\n")
            
            # Prepare messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Convert MCP tools to Anthropic tool format
            available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools.tools
            ]
            
            print("🤖 Claude is thinking...\n")
            
            # Call Claude with the tools
            response = anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=available_tools,
                messages=messages
            )
            
            # Process Claude's response
            while response.stop_reason == "tool_use":
                # Claude wants to use a tool
                tool_use = next(block for block in response.content if block.type == "tool_use")
                
                print(f"🔧 Calling tool: {tool_use.name}")
                print(f"   Parameters: {tool_use.input}\n")
                
                # Call the tool via MCP
                result = await session.call_tool(tool_use.name, tool_use.input)
                
                # Add tool result to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result.content
                        }
                    ]
                })
                
                # Continue the conversation
                response = anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    tools=available_tools,
                    messages=messages
                )
            
            # Extract final text response
            final_response = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "No response generated"
            )
            
            print("=" * 60)
            print("📊 ANSWER:")
            print("=" * 60)
            print(final_response)
            print("=" * 60)


async def interactive_mode():
    """
    Run an interactive session where user can ask multiple questions.
    """
    print("\n" + "=" * 60)
    print("🌤️  WEATHER MCP CLIENT - Interactive Mode")
    print("=" * 60)
    print("\nAsk weather questions like:")
    print("  • What's the weather in London?")
    print("  • Will it rain in Tokyo tomorrow?")
    print("  • Give me the forecast for Paris")
    print("\nType 'quit' or 'exit' to stop.\n")
    print("=" * 60 + "\n")
    
    while True:
        try:
            query = input("❓ Your question: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            await run_weather_query(query)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


async def main():
    """
    Main entry point for the client.
    Supports both single query and interactive modes.
    """
    if len(sys.argv) > 1:
        # Single query mode from command line arguments
        query = " ".join(sys.argv[1:])
        await run_weather_query(query)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())