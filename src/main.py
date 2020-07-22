"""
covidcast rest wrapper
"""
from enum import Enum
from typing import List, Dict, Union, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
import aiohttp
import asyncio

from model import MetaData, SignalData, SignalType, signal_to_data_source, TimeType, DateType, GeoType

app = FastAPI()
session = aiohttp.ClientSession()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URL = "https://api.covidcast.cmu.edu/epidata/api.php"

# covidcast.signal(data_source, signal, start_day=None, end_day=None, geo_type='county', geo_values='*')¶

def _format_date(d: date) -> str:
    return d.strftime('%Y%m%d')


def _format_params(params: Dict[str, Any]) -> Dict[str, str]:
    def _format_value(v: Any) -> str:
        if isinstance(v, list):
            return ','.join([_format_value(vi) for vi in v])
        if isinstance(v, Enum):
            return v.value
        if isinstance(v, date):
            return _format_date(v)
        if isinstance(v, bool):
            return 'true' if v else 'false'
        return str(v)
    return {k: _format_value(v) for k, v in params.items()}


async def _fetch(params: Dict[str, Union[str, int, float, date, List[str], List[int], List[float], List[date]]]):
    params['cached'] = True
    async with session.get(URL, params=_format_params(params)) as resp:
        print(resp.url)
        res = await resp.json()
        result = res.get('result', 0)
        if result == -2:
            raise HTTPException(status_code=400, detail=f"no results: {resp.url}")
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

def _get_day_offset(days=1) -> date:
    today = date.today()
    return today - timedelta(days=days)

@app.get('/signal', response_model=List[SignalData])
async def get_generic_signal(data_source: str, signal: str, time_type: TimeType, geo_type: GeoType, time_values: Optional[str] = None, geo_value: str = '*'):
    """
    return the raw meta data
    """
    return await _fetch({
        'source': 'covidcast',
        'data_source': data_source,
        'signal': signal,
        'time_type': time_type,
        'geo_type': geo_type,
        'time_values': time_values or _get_day_offset(2),
        'geo_value': geo_value
    })

@app.get('/signal/{signal}', response_model=List[SignalData])
async def get_signal(signal: SignalType, time_type: TimeType, geo_type: GeoType, time_values: Optional[List[date]] = Query(None), geo_value: str = '*'):
    """
    return the raw meta data
    :param signal
    :geo_value
    """
    source = signal_to_data_source[signal]
    return await _fetch({
        'source': 'covidcast',
        'data_source': source,
        'signal': signal,
        'time_type': time_type,
        'geo_type': geo_type,
        'time_values': time_values or [_get_day_offset(2)],
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