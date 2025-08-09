#!/usr/bin/env python3
"""
Test script for the tic-tac-toe MCP server.

To run this test:
1. Make sure you have the MCP server dependencies installed
2. Run the test script:
   python test.py

This will start the MCP server as a subprocess and interact with it over stdio,
testing a complete game sequence including:
- Starting a new game
- Making moves
- Showing the board after each move
- Testing error conditions
- Playing until game completion
"""

import asyncio


async def test_tic_tac_toe():
    pass

async def main():
    """Main test function."""
    await test_tic_tac_toe()


if __name__ == "__main__":
    asyncio.run(main())