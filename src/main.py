"""
covidcast rest wrapper
"""
from enum import Enum
from typing import List, Dict, Union, Optional, Any
from datetime import date, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp


class SignalType(str, Enum):
    """
    signal
    """

    smoothed_adj_cli = 'smoothed_adj_cli'
    """
    Doctor’s Visits
    """
    smoothed_adj_covid19 = 'smoothed_adj_covid19'
    """
    Hospital Admissions
    """
    smoothed_cli = 'smoothed_cli'
    """
    Symptoms (Facebook)
    """
    smoothed_hh_cmnty_cli = 'smoothed_hh_cmnty_cli'
    """
    Symptoms in Community (Facebook)
    """
    full_time_work_prop = 'full_time_work_prop'
    """
    Away from Home 6hr+ (SafeGraph)
    """
    part_time_work_prop = 'part_time_work_prop'
    """
    Away from Home 3-6hr (SafeGraph)
    """
    smoothed_search = 'smoothed_search'
    """
    Search Trends (Google)
    """
    nmf_day_doc_fbc_fbs_ght = 'nmf_day_doc_fbc_fbs_ght'
    """
    Combined
    """
    confirmed_7dav_incidence_num = 'confirmed_7dav_incidence_num'
    """
    Cases
    """
    confirmed_7dav_incidence_prop = 'confirmed_7dav_incidence_prop'
    """
    Cases per 100,000 People
    """
    deaths_7dav_incidence_num = 'deaths_7dav_incidence_num'
    """
    Deaths
    """
    deaths_7dav_incidence_prop = 'deaths_7dav_incidence_prop'
    """
    Deaths per 100,000 People
    """

class DataSourceType(str, Enum):
    """
    data sources
    """
    doctor_visits = 'doctor-visits'
    hospital_admission = 'hospital-admissions'
    fb_survey = 'fb-survey'
    safegraph = 'safegraph'
    ght = 'ght'
    indicator_combination = 'indicator-combination'

signal_to_data_source = {
    SignalType.smoothed_adj_cli: 'doctor-visits',
    SignalType.smoothed_adj_covid19: 'hospital-admissions',
    SignalType.smoothed_cli: 'fb-survey',
    SignalType.smoothed_hh_cmnty_cli : 'fb-survey',
    SignalType.full_time_work_prop: 'safegraph',
    SignalType.part_time_work_prop : 'safegraph',
    SignalType.smoothed_search : 'ght',
    SignalType.nmf_day_doc_fbc_fbs_ght : 'indicator-combination',
    SignalType.confirmed_7dav_incidence_num : 'indicator-combination',
    SignalType.confirmed_7dav_incidence_prop : 'indicator-combination',
    SignalType.deaths_7dav_incidence_num : 'indicator-combination',
    SignalType.deaths_7dav_incidence_prop : 'indicator-combination',
}

class TimeType(str, Enum):
    """
    time type
    """
    day = "day"
    week = "week"

class GeoType(str, Enum):
    """
    geo type
    """
    county = "county"
    hrr = 'hrr'
    msa = 'msa'
    dma = 'dma'
    state = 'state'


class MetaData(BaseModel):
    """
    meta  data
    """

    data_source: str
    """
    data source name
    """
    signal: str
    """
    signal name
    """
    time_type: TimeType
    """
    Temporal resolution at which this signal is reported. “day”,
    for example, means the signal is reported daily.
    """
    geo_type: GeoType
    """
    Geographic level for which this signal is available, such as county,
    state, msa, or hrr. Most signals are available at multiple geographic
    levels and will hence be listed in multiple rows with their own metadata.
    """
    min_time: int
    """
    First day for which this signal is available.
    """
    max_time: int
    """
    Most recent day for which this signal is available.
    """
    num_locations: int
    """
    Number of distinct geographic locations available for this signal.
    For example, if geo_type is county, the number of counties for which
    this signal has ever been reported.
    """
    min_value: float
    """
    The smallest value that has ever been reported.
    """
    max_value: float
    """
    The largest value that has ever been reported.
    """
    mean_value: float
    """
    The arithmetic mean of all reported values.
    """
    stdev_value: float
    """
    The sample standard deviation of all reported values.
    """
    last_update: int
    """
    """
    max_issue: int
    """
    """
    min_lag: int
    """
    """
    max_lag: int


class SignalData(BaseModel):
    """
    signal data
    """

    geo_value: str
    """
    identifies the location, such as a state name or county FIPS code.
    """
    time_value: int
    """
    contains a pandas Timestamp object identifying the date of this observation.
    """
    value: float
    """
    the signal quantity requested. For example, in a query for the
    confirmed_cumulative_num signal from the usa-facts source,
    this would be the cumulative number of confirmed cases in the area, as of the time_value.
    """
    stderr: Optional[float]
    """
    the signal’s standard error, if available.
    """
    sample_size: Optional[int]
    """
    indicates the sample size available in that geography on that day;
    sample size may not be available for all signals, due to privacy or other constraints.
    """
    direction: Optional[int]
    """
    uses a local linear fit to estimate whether the signal in this
    region is currently increasing or decreasing (reported as -1 for decreasing,
    1 for increasing, and 0 for neither).
    """
    lag: int
    issue: int



app = FastAPI()
# session = aiohttp.ClientSession()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URL = "https://api.covidcast.cmu.edu/epidata/api.php"

# covidcast.signal(data_source, signal, start_day=None, end_day=None, geo_type='county', geo_values='*')¶

def _format_date(date_obj: date) -> str:
    return date_obj.strftime('%Y%m%d')


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

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, params=_format_params(params)) as resp:
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
    return the signal values
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


@app.get('/signal/{signal}/range', response_model=List[SignalData])
async def get_signal_range(signal: SignalType, time_type: TimeType, geo_type: GeoType, from_time: date, to_time: date, geo_value: str = '*'):
    """
    return the signal values given a time range
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
        'time_values': f"{_format_date(from_time)}-{_format_date(to_time)}",
        'geo_value': geo_value
    })



@app.get("/")
def root():
    """
    main api endpoint
    """
    return {"message": "Hello World"}


# @app.on_event("shutdown")
# async def cleanup():
#     """
#     cleanup session
#     """
#     await session.close()
