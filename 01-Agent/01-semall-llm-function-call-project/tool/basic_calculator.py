"""Tool: basic_calculator — 支持加减乘除的简单计算器。"""

SUPPORTED_OPS = ("add", "subtract", "multiply", "divide")



def basic_calculator(operation: str, a: float, b: float) -> str:
    """执行四则运算，返回带算式的结果字符串"""
    op = (operation or "").strip().lower()
    if op not in SUPPORTED_OPS:
        return f"ERROR: unsupported operation '{operation}'"
    if op == "add":
        result = a + b
        expr = f"{a} + {b} = {result}"
    elif op == "subtract":
        result = a - b
        expr = f"{a} - {b} = {result}"
    elif op == "multiply":
        result = a * b
        expr = f"{a} × {b} = {result}"
    else:  # divide
        if b == 0:
            return "ERROR: division by zero"
        result = a / b
        expr = f"{a} ÷ {b} = {result}"

    return expr

SCHEMA = {
    "type": "function",
    "function": {
        "name": "basic_calculator",
        "description": "一个支持加减乘除的简单计算器，当需要用到加减乘除时使用",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "操作码，只能是add, subtract, multiply, divide中一个",
                },
                "a": {
                    "type": "number",
                    "description": "第一个操作数。",
                },
                "b": {
                    "type": "number",
                    "description": "第二个操作数。",
                },
            },
            "required": ["operation", "a", "b"],
            "additionalProperties": False,
        },
    },
}