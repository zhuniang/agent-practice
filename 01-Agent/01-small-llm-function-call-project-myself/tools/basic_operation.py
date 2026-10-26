"""TOOL: achieve basic operation ,such as: add,subtract,multiply,divide"""

VAILD_OPERATION=("add","subtract","multiply","divide")

SCHEMA = {
    "type": "function",
    "function": {
        "name": "basic_operation",
        "description": "基础四则运算工具，实现加减乘除，在需要用到时调用",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ['add','subtract','multiply','divide'],
                    "description": "操作码，仅限'add','subtract','multiply','divide'",
                },
                "a": {
                    "type" :"number",
                    "description": "第一个操作数",
                },
                "b": {
                    "type" :"number",
                    "description": "第二个操作数",
                },
            },
            "required": ["operation","a","b"]
        }
    }
}

def basic_operation(operation: str, a: float, b: float) -> str:
    """四则运算工具，返回结果字符串

    Args:
        operation (str): _description_
        a (float): _description_
        b (float): _description_

    Returns:
        str: _description_
    """
    
    if operation not in VAILD_OPERATION:
        return f"请输入正确的操作码"
    if operation == "add":
        return f"{a} add {b} = {a+b}"
    elif operation == "subtract":
        return f"{a} subtract {b} = {a-b}"
    elif operation == "divide":
        if b == 0:
            return f"除数不能为0"
        return f"{a} divide {b} = {a/b}"
    else :
        return f"{a} multiply {b} = {a*b}"
    
    
