import json
from operator import call
from pickle import TRUE
from random import randint
import subprocess
import os
from click import argument
from posthog import send

from main import new_game


def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Mac/Linux
    else:
        os.system('clear')

def send_message(proc, message,flag = TRUE):
    """Send a JSON-RPC message to the MCP server and return the parsed response."""
    # print(message)
    proc.stdin.write(json.dumps(obj=message) + "\n")
    proc.stdin.flush()
    if(flag):
        response = proc.stdout.readline()
        return json.loads(response)
    else :
        return None

# Start the MCP server as a subprocess (STDIN/STDOUT)
proc = subprocess.Popen(
    ["python3", "main.py"],  # <-- your server file here
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def initialize_server():
    # Step 1: Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "my-client",
                "version": "1.0.0"
            },
            "capabilities": {}
        }
    }

    print("Initializing...")
    init_response = send_message(proc, init_request)
    # print("Init response:", json.dumps(init_response, indent=2))

    # Step 2: Send "initialized" notification (MCP style)
    initialized_msg = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    send_message(proc, initialized_msg,False)  # No response expected

    print("\nMCP handshake complete!\n")

def get_tools():
    # Step 3: Get tool list
    tools_list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    return send_message(proc, tools_list_request)

def get_tool_names(tools_response):
    """Extract all tool names from the MCP tools/list response."""
    tools_list = tools_response.get("result", {}).get("tools", [])
    return [tool["name"] for tool in tools_list]

def build_tool_request(tool_name:str, tools_response,request_id=100,args = []):# -> None | dict[str, Any]:
    """Build a JSON-RPC request for the given tool using its input schema."""
    # Get the tools list
    tools_list = tools_response.get("result", {}).get("tools", [])
    # Find matching tool
    tool = next((t for t in tools_list if t["name"] == tool_name), None)
    if not tool:
        print(f"Tool '{tool_name}' not found.")
        return None
    
    # Get schema details
    schema = tool.get("inputSchema", {})
    props = schema.get("properties", {})
    required = schema.get("required", [])
    
    params = {}
    for (prop_name, prop_schema), arg in zip(props.items(), args):
        # print(f"prop_name: {prop_name}")
        # print(f"prop_schema: {prop_schema}")
        # print(f"arg: {arg}")
        if arg == '':
            if prop_name in required:
                print(f"'{prop_name}' is required.")
                return None
            else:
                continue  # skip optional param
        
        try:
            # Type conversion
            if prop_schema.get("type") == "integer":
                val = int(arg)
            elif prop_schema.get("type") == "number":
                val = float(arg)
            elif prop_schema.get("type") == "boolean":
                val = arg.lower() in ("true", "1", "yes")
            else:
                val = arg
        except ValueError:
            print(f"Invalid type for '{prop_name}'. Expected {prop_schema.get('type')}.")
            return None
        
        params[prop_name] = val
    
    # Return final JSON request
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name" : tool_name,
            "arguments" : params
        }
    }

def display_tool_response(response):
    """
    Extract and display the text from an MCP tool response.
    Assumes response['result']['content'] contains a list of dicts with 'type' and 'text'.
    """
    try:
        contents = response.get("result", {}).get("content", [])
        for item in contents:
            if item.get("type") == "text":
                print(item.get("text", ""))
    except Exception as e:
        print("Error extracting text from response:", e)

def choose_tool(tool_names):
    # Display numbered tool list
    print("Available tools:")
    for i, tool in enumerate(tool_names, start=1):
        print(f"{i}. {tool}")
    
    # Ask for number input
    choice = input(f"Select a tool by number (1-{len(tool_names)}) or 'quit': ").strip()
    
    if choice.lower() == "quit":
        return None
    
    # Validate choice
    if not choice.isdigit() or not (1 <= int(choice) <= len(tool_names)):
        print("Invalid selection. Please enter a valid number.")
        return choose_tool(tool_names)  # Ask again
    
    # Return selected tool name
    return tool_names[int(choice) - 1]

def new_game():
    return send_message(proc,build_tool_request("new_game",tools_response,randint(2,1000),['']))

def play_move(row,col):
    return send_message(proc,build_tool_request("play_move",tools_response,randint(2,1000),[row,col]))

def verify_game_result(response):
    rows = ["X | O | X","O | X | O","X |   |  "] 
    val = "\n" + "\n---------\n".join(rows)
    val = f"{val}\n\nWinner: X"
    res = response["result"]["content"][0]["text"]
    print(f"{val} \n")
    return val==res

def play_game():
    print("setting up new game\n")
    new_game()
    print("starting game\n")
    resp = {}
    for i in range(3):
        for j in range(3):
            if(i==2 and j>0):
                break
            res = play_move(i,j)
    print("game finished\n")
    success = verify_game_result(res)
    if(success) :
        print("Test Passed\n")
    else :
        print("Test Failed")
    return

initialize_server()
tools_response = get_tools()
tool_names = get_tool_names(tools_response)
play_game()
