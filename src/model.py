"""
covidcast rest wrapper
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SignalType(str, Enum):
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
    full_time_work_prop= 'full_time_work_prop'
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
    day = "day"
    week = "week"

class DateType(str, Enum):
    day = "day"
    week = "week"

class GeoType(str, Enum):
    county = "county"
    hrr = 'hrr'
    msa = 'msa'
    dma = 'dma'
    state = 'state'


class MetaData(BaseModel):
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
    Temporal resolution at which this signal is reported. “day”, for example, means the signal is reported daily.
    """
    geo_type: GeoType
    """
    Geographic level for which this signal is available, such as county, state, msa, or hrr. Most signals are available at multiple geographic levels and will hence be listed in multiple rows with their own metadata.
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
    Number of distinct geographic locations available for this signal. For example, if geo_type is county, the number of counties for which this signal has ever been reported.
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
    the signal quantity requested. For example, in a query for the confirmed_cumulative_num signal from the usa-facts source, this would be the cumulative number of confirmed cases in the area, as of the time_value.
    """
    stderr: Optional[float]
    """
    the signal’s standard error, if available.
    """
    sample_size: Optional[int]
    """
    indicates the sample size available in that geography on that day; sample size may not be available for all signals, due to privacy or other constraints.
    """
    direction: Optional[int]
    """
    uses a local linear fit to estimate whether the signal in this region is currently increasing or decreasing (reported as -1 for decreasing, 1 for increasing, and 0 for neither).
    """
    lag: int
    issue: int
