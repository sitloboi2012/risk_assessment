from __future__ import annotations
from unittest import result

import requests
import http
import asyncio
import aiohttp
import pandas as pd

def convert_from_list_to_dictionaries(list_1, list_2):
    result = {}
    for key, value in zip(list_1,list_2):
        result[key] = value
    return result

def binarize_image(image) -> list:
    return image_array_list

def similarity_classification(image_binarize):
    pass