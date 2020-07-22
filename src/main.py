"""
covidcast rest wrapper
"""
from enum import Enum
from typing import List, Dict, Union, Optional
from fastapi import FastAPI, HTTPException
from datetime import date, timedelta
import aiohttp
import asyncio

from model import MetaData, SignalData, SignalType, signal_to_data_source, TimeType, DateType, GeoType

app = FastAPI()
session = aiohttp.ClientSession()

url = "https://api.covidcast.cmu.edu/epidata/api.php"

# covidcast.signal(data_source, signal, start_day=None, end_day=None, geo_type='county', geo_values='*')¶

async def _fetch(params: Dict[str, Union[str, int, float]]):
    params['cached'] = 'true'
    print(str(params))
    string_params = {k: v.value if isinstance(v, Enum) else str(v) for k, v in params.items()}
    async with session.get(url, params=string_params) as resp:
        print(resp.url)
        res = await resp.json()
        result = res.get('result', 0)
        if result == -2:
            # no results
            return []
        if result != 1:
            raise HTTPException(status_code=500, detail=res["message"])
        return res.get("epidata", [])


@app.get('/metadata', response_model=List[MetaData])
async def metadata():
    """
    return the raw meta data
    """
    return await _fetch(dict(source="covidcast_meta"))


# :path: /epidata/api.php?source=covidcast&cached=true&
# data_source=indicator-combination&
# signal=confirmed_incidence_num&
# geo_type=county&
# time_values=20200716&
# time_type=day&
# geo_value=*

# time_values: a,b,a-b

def _get_day_offset(days = 1):
    today = date.today()
    day_of_before_yesterday = today - timedelta(days=days)
    return day_of_before_yesterday.strftime('%Y%m%d')

@app.get('/signal/{signal}', response_model=List[SignalData])
async def get_signal(signal: SignalType, time_type: TimeType, geo_type: GeoType, time_values: Optional[str] = None, geo_value: str = '*'):
    """
    return the raw meta data
    """
    time_values = time_values or _get_day_offset(2)
    source = signal_to_data_source[signal]
    return await _fetch({
        'source': 'covidcast',
        'data_source': source,
        'signal': signal,
        'time_type': time_type,
        'geo_type': geo_type,
        'time_values': time_values,
        'geo_value': geo_value
    })


@app.get("/")
def root():
    """
    main api endpoint
    """
    return {"message": "Hello World"}


@app.on_event("shutdown")
async def cleanup():
    await session.close()