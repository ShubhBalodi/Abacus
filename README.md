# MCP Project
In this project you will be developing an M(odel)C(ontext)P(rotocol) server to allow
an LLM to interact with a simple game. The question has multiple parts and you should
solve each part before progressing to the next one. There is no golden answer or
specific check that must be passed at each part but each part has a sensible goal and
you should be able to judge if your solution meets the goal.

Start here: https://github.com/modelcontextprotocol to learn about
the Model Context Protocol. Only look at the Python SDK since this project
is based on the Python MCP SDK.

## Instructions
You have been provided with:
- This initial repository that has instructions for setting up a working environment (see the README)
- An API key that can be used to access the Anthropic API

This project requires at least Python 3.11, ensure that the Python interpreter
you are using meets this requirement.

It is recommended you setup a venv to install the requirements for this project,
though that is not required.

Setup requires installing the sources in this project as editable modules.
You should be able to just run this command to get started.

```shell
pip install -e . mcp-use
```

Implement the following functionality in order:

## Problem

### Part 1: MCP Stdio Server

Implement an MCP server that manages the state for a game Tic-Tac-Toe. It should support:
- New game
- Show board (including who plays next or if the game is over the winner if any)
- Play move

Implement the MCP game server in `main.py`. The server should be a stdio server and
there is a simple starting file provided which you need to complete with the
game implementation. You should be able to test your game implementation directly
by piping JSON requests to:

```shell
echo <Some JSON> | python main.py
```

IMPORTANT: Implement this as an MCP stdio server (not an HTTP server)

### Part 2

Create a testing script that  simulates a full sequence of interactivity with the
MCP server you just implemented. Exercise all the functions:
- Play a game all the way through the end
- Print out all the interactions
- Check that the end state matches expectations
- Create a script `run_test.sh` that be executed to run your test.

The test script can be as simple as:
```shell
python test.py
```
if you implement the test by completing `test.py`.

### Part 3: Configure an MCP Client to Play

Now you are going to use your MCP server and prompt the LLM so that you can actually
play the game against the LLM. You can get started on testing your MCP with an LLM
using this simple script:

```shell
ANTHROPIC_API_KEY=<key> python python/chat.py
```

Modify `chat.py` so that the user can play the game against the LLM.
- The script is setup tp use Claude Haiku as the LLM
- Modify the implementation and system prompt so that it plays the ONE TURN of the game with the user.
- It should support playing the turn or applying the users move at that turn and displaying the result.
- Commit a script `send_messages.sh` that gives an example invocation.

### Part 4: MCP Server Persistence

You should have noticed that the LLM is confused because it appears that the game state resets every time
the client is invoked from the command line. That is because the MCP server is so far stateless.
In this step add support for state keeping.
- Save the state in a file after each operation so that it persists across invocations.
- Play against the LLM through the end
- Commit a script `play_game.sh` invoking the client through a full sequence of turns 


## Documenting your work

To aid in judging your work it is important to record the details of how you approached the problem:
- The documentation and tools you used to develop the solution
- Any command lines or scripts you used for debugging and testing your work
- Logs of commands you ran indicating that things were working
- Multiple commits capturing your incremental progress
It is easiest to share all of these through the repo, feel free to commit markdown files into the repo recording this information. Similarly, add temporary scripts and logs to the repository so we can review them.

*NOTE: Limit your solution to a Python implementation. Do not try to use languages. Shell scripts are ok for documenting python invocations.*

## Expected Outcome
At the end of your task all of your work should be committed to the repository provided. Include a `SOLUTION.md` in one of your commits explaining the tests added and instructions on how to run and any scripts you created. `SOLUTION.md` should also explain in detail how you used any AI tools to support your work and give some indication of what code was written with the assistance of AI. Ideally, your commit messages will reflect if a substantial portion of the commit was AI generated.

## Evaluation Criteria

| Criteria | Description |
|----------|-------------|
| Working scripts | Scripts that can run the implemented code |
| Use of AI | Effective use of AI to achieve the goal |
| Quality of code | Subjective assessment of implementation |
| Documentation | Description of implementation |
