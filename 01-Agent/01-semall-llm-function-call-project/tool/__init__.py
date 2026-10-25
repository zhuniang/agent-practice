"""工具注册中心"""
from tool.reverse_string import reverse_string
from tool.basic_calculator import basic_calculator
from tool.basic_calculator import SCHEMA as B_SCHEMA
from tool.reverse_string import SCHEMA as A_SCHEMA

TOOLS_REGISTRY: dict = {
    "reverse_string": reverse_string,
    "basic_calculator": basic_calculator
}

TOOLS = [A_SCHEMA,B_SCHEMA]
