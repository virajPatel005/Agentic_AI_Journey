import random
from fastmcp import FastMCP

mcp=FastMCP(name="Demo Server")

@mcp.tool()
def roll_dice(n_dice:int = 1) ->list[int]:
    """Roll 6 sided Dice n_dce times and return the result """
    return[random.randint(1,6)for i in range (n_dice)]

@mcp.tool()
def add_numbers(a:float,b:float) ->float:
    """Add two numbers together."""
    return a+b 

if __name__=="__main__":
    mcp.run()