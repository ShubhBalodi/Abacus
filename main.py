import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# -------------------
# Game Implementation
# -------------------
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.moves = 0

    def show_board(self) -> str:
        rows = [" | ".join(row) for row in self.board]
        board_str = "\n" + "\n---------\n".join(rows)
        if self.winner:
            return f"{board_str}\n\nWinner: {self.winner}"
        elif self.moves == 9:
            return f"{board_str}\n\nDraw!"
        else:
            return f"{board_str}\n\nNext: {self.current_player}"

    def play_move(self, row: int, col: int) -> str:
        if self.winner or self.moves == 9:
            return "Game over. Please start a new game."
        if not (0 <= row < 3 and 0 <= col < 3):
            return "Invalid move. Row and column must be 0, 1, or 2."
        if self.board[row][col] != " ":
            return "Invalid move. Cell already taken."
        self.board[row][col] = self.current_player
        self.moves += 1
        if self.check_winner(row, col):
            self.winner = self.current_player
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
        return self.show_board()

    def check_winner(self, row: int, col: int) -> bool:
        b = self.board
        p = self.current_player
        return (
            all(b[row][c] == p for c in range(3)) or
            all(b[r][col] == p for r in range(3)) or
            (row == col and all(b[i][i] == p for i in range(3))) or
            (row + col == 2 and all(b[i][2 - i] == p for i in range(3)))
        )

# -------------------
# MCP Tool Handlers
# -------------------
game = TicTacToe()

async def new_game():
    game.reset()
    return TextContent(type="text", text="New game started.\n" + game.show_board())

async def show_board():
    return TextContent(type="text", text=game.show_board())

async def play_move(row: int, col: int):
    return TextContent(type="text", text=game.play_move(row, col))

# -------------------
# MCP Tool Metadata
# -------------------
tool_list = [
    Tool(
        name="new_game",
        description="Start a new game of Tic-Tac-Toe",
        inputSchema={"type": "object", "properties": {}, "required": []}
    ),
    Tool(
        name="show_board",
        description="Show the current board and game state. Also shows the player who needs to make a move (ex- 'X' or 'O')",
        inputSchema={"type": "object", "properties": {}, "required": []}
    ),
    Tool(
        name="play_move",
        description="Play a move. Provide row and column (0-based).",
        inputSchema={
            "type": "object",
            "properties": {
                "row": {"type": "integer", "minimum": 0, "maximum": 2},
                "col": {"type": "integer", "minimum": 0, "maximum": 2}
            },
            "required": ["row", "col"]
        }
    )
]

tool_handlers = {
    "new_game": lambda args: new_game(),
    "show_board": lambda args: show_board(),
    "play_move": lambda args: play_move(args["row"], args["col"])
}

# -------------------
# MCP Server
# -------------------
server = Server("tic-tac-toe")

@server.list_tools()
async def list_tools():
    return tool_list

@server.call_tool()
async def call_tool(name: str, arguments: dict | None):
    if arguments is None:
        arguments = {}
    handler = tool_handlers.get(name)
    if handler:
        return [await handler(arguments)]
    return [TextContent(type="text", text="Unknown tool")]

# -------------------
# Entry Point
# -------------------
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
