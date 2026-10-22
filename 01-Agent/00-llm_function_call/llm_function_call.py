from openai import OpenAI
from typing import Any,List
import json
from pprint import pprint
from dotenv import load_dotenv
from __future__ import annotations
import os
load_dotenv("D:\\projects\\AI-Engineer-from-scrach\\.env")
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)
def getWeather(city: str):
    mock_data={
        "北京":"19℃",
        "上海":"26℃"
    }
    city=city.strip()
    return mock_data.get(city,f"暂无{city}数据")

tools = [
    {
        ""
    }
]

SCHEMA=(
    ""
)






