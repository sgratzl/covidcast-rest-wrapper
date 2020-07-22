"""
covidcast rest wrapper
"""
from typing import List
from fastapi import FastAPI, HTTPException
import aiohttp
import asyncio
from model import MetaData, SignalData

app = FastAPI()
session = aiohttp.ClientSession()

url = "https://api.covidcast.cmu.edu/epidata/api.php"

# covidcast.signal(data_source, signal, start_day=None, end_day=None, geo_type='county', geo_values='*')¶

@app.get('/metadata', response_model=List[MetaData])
async def metadata():
    """
    return the raw meta data
    """
    async with session.get(url, params=dict(source="covidcast_meta", cached='true')) as resp:
        r = await resp.json()
        if not r['result']:
            raise HTTPException(status_code=500, detail="invalid result")
        return r["epidata"]



@app.get("/")
def root():
    """
    main api endpoint
    """
    return {"message": "Hello World"}


@app.on_event("shutdown")
async def cleanup():
    await session.close()