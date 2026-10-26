from tools.basic_operation import basic_operation, SCHEMA as B_SCHEMA
from tools.reverse_string import reverse_string, SCHEMA as A_SCHEMA

TOOLS = [A_SCHEMA,B_SCHEMA]

TOOLS_REGISTRY = {
    "basic_operation": basic_operation,
    "reverse_string": reverse_string,
}
