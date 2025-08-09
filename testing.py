import json
from operator import call
from pickle import TRUE
from random import randint
import subprocess
import os
from click import argument


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

# Step 3: Get tool list
tools_list_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

def get_tool_names(tools_response):
    """Extract all tool names from the MCP tools/list response."""
    tools_list = tools_response.get("result", {}).get("tools", [])
    return [tool["name"] for tool in tools_list]

tools_response = send_message(proc, tools_list_request)
tool_names = get_tool_names(tools_response)
# print("Available tools:", json.dumps(tools_response, indent=2))


def build_tool_request(tool_name, tools_response, request_id=100):
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
    
    for prop_name, prop_schema in props.items():
        while True:
            user_input = input(f"Enter value for '{prop_name}' ({prop_schema.get('type', 'string')}): ").strip()
            
            if not user_input:
                if prop_name in required:
                    print(f"'{prop_name}' is required.")
                    continue
                else:
                    break  # skip optional param
            
            try:
                # Type conversion
                if prop_schema.get("type") == "integer":
                    val = int(user_input)
                elif prop_schema.get("type") == "number":
                    val = float(user_input)
                elif prop_schema.get("type") == "boolean":
                    val = user_input.lower() in ("true", "1", "yes")
                else:
                    val = user_input
            except ValueError:
                print(f"Invalid type for '{prop_name}'. Expected {prop_schema.get('type')}.")
                continue
            
            params[prop_name] = val
            break
    
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

# Step 4: Interactive tool calls
while True:
    try:
        # method = input(f"Which tool would you like to use? ({', '.join(tool_names)}): (or 'quit') ").strip()
        method = choose_tool(tool_names)
        clear_screen()
        if method is None:
            proc.kill()
            break

        request = build_tool_request(method.lower(),tools_response,randint(2,100))
        # print(request)
        # params_raw = input("Params as JSON (e.g. {\"name\": \"Alice\"}): ").strip()
        # params = json.loads(params_raw) if params_raw else {}

        # request_id = 100  # arbitrary
        # request = {
        #     "jsonrpc": "2.0",
        #     "id": request_id,
        #     "method": method,
        #     "params": params
        # }

        response = send_message(proc, request)
        display_tool_response(response)
        # print("Response:", json.dumps(response, indent=2))

    except Exception as e:
        print("Error:", e)
