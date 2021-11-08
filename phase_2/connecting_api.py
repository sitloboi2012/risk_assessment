from __future__ import annotations
from nbformat import from_dict
from phase_2.utilities import *


import json
import asyncio
import aiohttp

HEADERS = {"Accept": "application/json"}


async def _connecting_fda_recall(ORGANISATION_NAME, CITY)-> bytes:
    """Connecting to FDA Recall Database to pull the information about recall product

    Args:
        ORGANISATION_NAME ([str]): the organisation name that extract from FSSC/BRC document
        CITY ([str]): the city name that extract from FSSC/BRC document

    Returns:
        [bytes]: coroutine object contains bytes information from database
    """
    
    API_KEY = "er866eX0tAEwP5BwohWDaYGkWrSJrJpBkZ8Re46j"
    PRODUCT_TYPE = "FOOD"
    LIMIT_APPEAR = 100
    URL = f"https://api.fda.gov/food/enforcement.json?api_key={API_KEY}&limit={LIMIT_APPEAR}&search=city:{CITY}+recalling_firm:{ORGANISATION_NAME}+AND+product_type:{PRODUCT_TYPE}"

    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            database = await response.read()
            return database

async def get_info_database(ORGANISATION_NAME, CITY) -> list:
    """Extract the info from the database and get the stuff we need

    Args:
        ORGANISATION_NAME (str): the organisation name extract from FSSC/BRC document
        CITY (str): the city name extract from FSSC/BRC document

    Returns:
        list: dictionaries in a list that contain key information to do analysis
    """
    list_of_key = ["recalling_firm", "state", 
                   "reason_for_recall", "status",
                   "distribution_pattern", "product_description",
                   "recall_initiation_date", "classification"]
    
    async with aiohttp.ClientSession():
        html = await _connecting_fda_recall(ORGANISATION_NAME, CITY)
        response = from_dict(json.loads(html.decode("utf-8"))["results"])
        #extracted_value = [response.get(key) for key in list_of_key]
        #result = convert_from_list_to_dictionaries(list_of_key, extracted_value)
    
        return response

def get_adverse_events():
    pass

def connecting_fdc_database():
    pass

def main_phase_2(ORGANISATION_NAME, CITY):
    loop = asyncio.new_event_loop() 
    asyncio.set_event_loop(loop)
    value = loop.run_until_complete(get_info_database(ORGANISATION_NAME, CITY))
    return value

#if __name__ == "__main__":
#    main()