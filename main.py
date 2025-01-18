import json
from pathlib import Path
import asyncio
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly_style import dark_template

from btcli.bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface
from btcli.bittensor_cli.src.bittensor.balances import Balance


app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:1420",
    "https://localhost:1420",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    return {"Info": "Bittensor Subnet Price API"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


async def price(
    subtensor: "SubtensorInterface",
    netuid: int,
    interval_hours: int = 24,
):
    """Fetch historical subnet price data and return as JSON."""
    
    blocks_per_hour = int(3600 / 12)  # ~300 blocks per hour
    total_blocks = blocks_per_hour * interval_hours

    # Fetch data
    current_block_hash = await subtensor.substrate.get_chain_head()
    current_block = await subtensor.substrate.get_block_number(current_block_hash)

    # Block range  
    step = 300
    start_block = max(0, current_block - total_blocks)
    block_numbers = range(start_block, current_block + 1, step)

    # Fetch all block hashes
    block_hash_cors = [
        subtensor.substrate.get_block_hash(bn) for bn in block_numbers
    ]
    block_hashes = await asyncio.gather(*block_hash_cors)

    # Fetch subnet data for each block
    subnet_info_cors = [
        subtensor.get_subnet_dynamic_info(netuid, bh) for bh in block_hashes
    ]
    subnet_infos = await asyncio.gather(*subnet_info_cors)

    # Process data
    price_data = []
    for block_num, subnet_info in zip(block_numbers, subnet_infos):
        if subnet_info is not None:
            price_data.append({
                "block": block_num,
                "price": float(subnet_info.price.tao),
                "unit": Balance.get_unit(netuid)
            })

    return {
        "netuid": netuid,
        "interval_hours": interval_hours,
        "data_points": len(price_data),
        "prices": price_data
    }


# @app.get("/price_data")
# async def get_price_data(netuid: int = 277, interval_hours: int = 24):
#     """Get historical price data for a subnet"""
#     try:
#         subtensor = SubtensorInterface("test")
#         async with subtensor:
#             result = await price(subtensor, netuid, interval_hours)
#             return result
#     except Exception as e:
#         return JSONResponse(
#             content={"error": str(e)}, 
#             status_code=500
#         )


@app.get("/price_chart") 
async def get_price_chart(netuid: int = 277, interval_hours: int = 24):
    """Get price chart for a subnet"""
    try:
        subtensor = SubtensorInterface("test")
        async with subtensor:
            result = await price(subtensor, netuid, interval_hours)
            
            # Create DataFrame
            df = pd.DataFrame(result["prices"])
            
            # Create plot
            fig = go.Figure(
                data=[go.Scatter(
                    x=df["block"],
                    y=df["price"],
                    mode='lines',
                    name='Price'
                )],
                layout=go.Layout(
                    template=dark_template,
                    title=f"Subnet {netuid} Price History",
                    xaxis_title="Block Number",
                    yaxis_title=f"Price ({result['prices'][0]['unit']})"
                )
            )
            
            return json.loads(fig.to_json())
            
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    try:
        import bittensor
        print("Bittensor version:", bittensor.__version__)
    except ImportError as e:
        print("Failed to import bittensor:", e)
        
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5050)