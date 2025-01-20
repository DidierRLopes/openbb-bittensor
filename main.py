import json
from pathlib import Path
import asyncio
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly_style import dark_template
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

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

SUBNETS_LIST = [
  {"label": "SN1 - Apex", "value": 1},
  {"label": "SN2 - Omron", "value": 2},
  {"label": "SN3 - Templar", "value": 3},
  {"label": "SN4 - Targon", "value": 4},
  {"label": "SN5 - Kaito", "value": 5},
  {"label": "SN6 - Infinite Games", "value": 6},
  {"label": "SN7 - Subvortex", "value": 7},
  {"label": "SN8 - Taoshi", "value": 8},
  {"label": "SN9 - Pre-Training", "value": 9},
  {"label": "SN10 - Sturdy", "value": 10},
  {"label": "SN11 - Dippy", "value": 11},
  {"label": "SN12 - Horde", "value": 12},
  {"label": "SN13 - Data Universe", "value": 13},
  {"label": "SN14 - Paladin", "value": 14},
  {"label": "SN15 - De_Val", "value": 15},
  {"label": "SN16 - BitAds", "value": 16},
  {"label": "SN17 - Three Gen", "value": 17},
  {"label": "SN18 - Cortex.t", "value": 18},
  {"label": "SN19 - Inference", "value": 19},
  {"label": "SN20 - BitAgent", "value": 20},
  {"label": "SN21 - Omega", "value": 21},
  {"label": "SN22 - Metasearch", "value": 22},
  {"label": "SN23 - SocialTensor", "value": 23},
  {"label": "SN24 - Omega 2", "value": 24},
  {"label": "SN25 - Protein Folding", "value": 25},
  {"label": "SN26 - Tensor Alchemy", "value": 26},
  {"label": "SN27 - Compute", "value": 27},
  {"label": "SN28 - S&P500", "value": 28},
  {"label": "SN29 - ColdInt", "value": 29},
  {"label": "SN30 - Bettensor", "value": 30},
  {"label": "SN31 - NASChain", "value": 31},
  {"label": "SN32 - It's AI", "value": 32},
  {"label": "SN33 - ReadyAI", "value": 33},
  {"label": "SN34 - BitMind", "value": 34},
  {"label": "SN35 - LogicNet", "value": 35},
  {"label": "SN36 - WOMBO", "value": 36},
  {"label": "SN37 - Finetuning", "value": 37},
  {"label": "SN38 - DTS", "value": 38},
  {"label": "SN39 - EdgeMAxxing", "value": 39},
  {"label": "SN40 - Chunking", "value": 40},
  {"label": "SN41 - Sportstensor", "value": 41},
  {"label": "SN42 - Masa", "value": 42},
  {"label": "SN43 - Graphite", "value": 43},
  {"label": "SN44 - Score", "value": 44},
  {"label": "SN45 - Gen42", "value": 45},
  {"label": "SN46 - NeuralAI", "value": 46},
  {"label": "SN47 - CondenseAI", "value": 47},
  {"label": "SN48 - Nextplace", "value": 48},
  {"label": "SN49 - Hivebrain", "value": 49},
  {"label": "SN50 - No Data", "value": 50},
  {"label": "SN51 - Compute", "value": 51},
  {"label": "SN52 - Dojo", "value": 52},
  {"label": "SN53 - Effi", "value": 53},
  {"label": "SN54 - Brainlock", "value": 54},
  {"label": "SN55 - Precog", "value": 55},
  {"label": "SN56 - Gradient", "value": 56},
  {"label": "SN57 - Gaia", "value": 57},
  {"label": "SN58 - Dippy Speech", "value": 58},
  {"label": "SN59 - AgentArena", "value": 59},
  {"label": "SN60 - No Data", "value": 60},
  {"label": "SN61 - Redteam", "value": 61},
  {"label": "SN62 - Agentao", "value": 62},
  {"label": "SN63 - No Data", "value": 63},
  {"label": "SN64 - Chutes", "value": 64},
  {"label": "SN65", "value": 65},
  {"label": "SN66", "value": 66},
  {"label": "SN67", "value": 67},
  {"label": "SN68", "value": 68},
  {"label": "SN69", "value": 69},
  {"label": "SN70", "value": 70},
  {"label": "SN71", "value": 71},
  {"label": "SN72", "value": 72},
  {"label": "SN73", "value": 73},
  {"label": "SN74", "value": 74},
  {"label": "SN75", "value": 75},
  {"label": "SN76", "value": 76},
  {"label": "SN77", "value": 77},
  {"label": "SN78", "value": 78},
  {"label": "SN79", "value": 79},
  {"label": "SN80", "value": 80},
  {"label": "SN81", "value": 81},
  {"label": "SN82", "value": 82},
  {"label": "SN83", "value": 83},
  {"label": "SN84", "value": 84},
  {"label": "SN85", "value": 85},
  {"label": "SN86", "value": 86},
  {"label": "SN87", "value": 87},
  {"label": "SN88", "value": 88},
  {"label": "SN89", "value": 89},
  {"label": "SN90", "value": 90},
  {"label": "SN91", "value": 91},
  {"label": "SN92", "value": 92},
  {"label": "SN93", "value": 93},
  {"label": "SN94", "value": 94},
  {"label": "SN95", "value": 95},
  {"label": "SN96", "value": 96},
  {"label": "SN97", "value": 97},
  {"label": "SN98", "value": 98},
  {"label": "SN99", "value": 99},
  {"label": "SN100", "value": 100},
  {"label": "SN101", "value": 101},
  {"label": "SN102", "value": 102},
  {"label": "SN103", "value": 103},
  {"label": "SN104", "value": 104},
  {"label": "SN105", "value": 105},
  {"label": "SN106", "value": 106},
  {"label": "SN107", "value": 107},
  {"label": "SN108", "value": 108},
  {"label": "SN109", "value": 109},
  {"label": "SN110", "value": 110},
  {"label": "SN111", "value": 111},
  {"label": "SN112", "value": 112},
  {"label": "SN113", "value": 113},
  {"label": "SN114", "value": 114},
  {"label": "SN115", "value": 115},
  {"label": "SN116", "value": 116},
  {"label": "SN117", "value": 117},
  {"label": "SN118", "value": 118},
  {"label": "SN119", "value": 119},
  {"label": "SN120", "value": 120},
  {"label": "SN121", "value": 121},
  {"label": "SN122", "value": 122},
  {"label": "SN123", "value": 123},
  {"label": "SN124", "value": 124},
  {"label": "SN125", "value": 125},
  {"label": "SN126", "value": 126},
  {"label": "SN127", "value": 127},
  {"label": "SN128", "value": 128},
  {"label": "SN129", "value": 129},
  {"label": "SN130", "value": 130},
  {"label": "SN131", "value": 131},
  {"label": "SN132", "value": 132},
  {"label": "SN133", "value": 133},
  {"label": "SN134", "value": 134},
  {"label": "SN135", "value": 135},
  {"label": "SN136", "value": 136},
  {"label": "SN137", "value": 137},
  {"label": "SN138", "value": 138},
  {"label": "SN139", "value": 139},
  {"label": "SN140", "value": 140},
  {"label": "SN141", "value": 141},
  {"label": "SN142", "value": 142},
  {"label": "SN143", "value": 143},
  {"label": "SN144", "value": 144},
  {"label": "SN145", "value": 145},
  {"label": "SN146", "value": 146},
  {"label": "SN147", "value": 147},
  {"label": "SN148", "value": 148},
  {"label": "SN149", "value": 149},
  {"label": "SN150", "value": 150},
  {"label": "SN151", "value": 151},
  {"label": "SN152", "value": 152},
  {"label": "SN153", "value": 153},
  {"label": "SN154", "value": 154},
  {"label": "SN155", "value": 155},
  {"label": "SN156", "value": 156},
  {"label": "SN157", "value": 157},
  {"label": "SN158", "value": 158},
  {"label": "SN159", "value": 159},
  {"label": "SN160", "value": 160},
  {"label": "SN161", "value": 161},
  {"label": "SN162", "value": 162},
  {"label": "SN163", "value": 163},
  {"label": "SN164", "value": 164},
  {"label": "SN165", "value": 165},
  {"label": "SN166", "value": 166},
  {"label": "SN167", "value": 167},
  {"label": "SN168", "value": 168},
  {"label": "SN169", "value": 169},
  {"label": "SN170", "value": 170},
  {"label": "SN171", "value": 171},
  {"label": "SN172", "value": 172},
  {"label": "SN173", "value": 173},
  {"label": "SN174", "value": 174},
  {"label": "SN175", "value": 175},
  {"label": "SN176", "value": 176},
  {"label": "SN177", "value": 177},
  {"label": "SN178", "value": 178},
  {"label": "SN179", "value": 179},
  {"label": "SN180", "value": 180},
  {"label": "SN181", "value": 181},
  {"label": "SN182", "value": 182},
  {"label": "SN183", "value": 183},
  {"label": "SN184", "value": 184},
  {"label": "SN185", "value": 185},
  {"label": "SN186", "value": 186},
  {"label": "SN187", "value": 187},
  {"label": "SN188", "value": 188},
  {"label": "SN189", "value": 189},
  {"label": "SN190", "value": 190},
  {"label": "SN191", "value": 191},
  {"label": "SN192", "value": 192},
  {"label": "SN193", "value": 193},
  {"label": "SN194", "value": 194},
  {"label": "SN195", "value": 195},
  {"label": "SN196", "value": 196},
  {"label": "SN197", "value": 197},
  {"label": "SN198", "value": 198},
  {"label": "SN199", "value": 199},
  {"label": "SN200", "value": 200},
  {"label": "SN201", "value": 201},
  {"label": "SN202", "value": 202},
  {"label": "SN203", "value": 203},
  {"label": "SN204", "value": 204},
  {"label": "SN205", "value": 205},
  {"label": "SN206", "value": 206},
  {"label": "SN207", "value": 207},
  {"label": "SN208", "value": 208}
]


# Add after app initialization
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


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

@app.get("/subnets")
def get_subnets():
    """Returns list of all subnets with their labels and values"""
    return SUBNETS_LIST

@app.get("/price_data")
async def get_price_data(netuid: int = 1, interval_hours: int = 24):
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

# @cache(expire=300)  # Cache for 5 minutes
@app.get("/price_data_multiple")
async def get_price_data_multiple(netuid: str = "", interval_hours: int = 24):
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
                    combined[block][SUBNETS_LIST[netuid-1]["label"]] = data["price"]
            
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