import json
from pathlib import Path
import asyncio
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly_style import dark_template
from typing import List

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
                # "unit": Balance.get_unit(netuid)
            })

    return price_data


@app.get("/price_data")
async def get_price_data(netuid: int = 277, interval_hours: int = 24):
    """Get historical price data for a subnet"""
    try:
        subtensor = SubtensorInterface("test")
        async with subtensor:
            result = await price(subtensor, netuid, interval_hours)
            return result
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)}, 
            status_code=500
        )

@app.get("/price_data_multiple")
async def get_price_data_multiple(netuid: str = "1,2", interval_hours: int = 24):
    """Get historical price data for multiple subnets"""
    try:
        # Parse comma-separated string into list of integers
        netuid_list = [int(n.strip()) for n in netuid.split(",")]

        subtensor = SubtensorInterface("test")
        async with subtensor:
            # Get price data for each subnet
            results = await asyncio.gather(*[
                price(subtensor, netuid, interval_hours) 
                for netuid in netuid_list
            ])
            
            # Combine results by block number
            combined = {}
            for netuid, result in zip(netuid_list, results):
                for data in result:
                    block = data["block"]
                    if block not in combined:
                        combined[block] = {"block": block}
                    combined[block][f"price_sn{netuid}"] = data["price"]
            
            # Convert to list sorted by block
            combined_list = list(combined.values())
            combined_list.sort(key=lambda x: x["block"])
            
            return combined_list
            
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)}, 
            status_code=500
        )


@app.get("/price_chart") 
async def get_price_chart(netuid: int = 277, interval_hours: int = 24):
    """Get price chart for a subnet"""
    try:
        subtensor = SubtensorInterface("test")
        async with subtensor:
            result = await price(subtensor, netuid, interval_hours)
            
            # Create DataFrame
            df = pd.DataFrame(result)
            
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
                    yaxis_title="Price"
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