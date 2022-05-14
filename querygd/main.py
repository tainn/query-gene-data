import os

from fastapi import FastAPI

import impl
from models import GeneSequence

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = FastAPI()


@app.get("/data")
async def get_data(q: str) -> GeneSequence:
    """Receives either an ID or a combination of CHROM and POS and returns the corresponding row values."""

    return await impl.get_data(q)
