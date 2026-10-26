"""TOOL: achieve string reverse"""

SCHEMA = {
    "type": "function",
    "function": {
        "name": "reverse_string",
        "description": "反转字符串工具，在需要用到时调用",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "字符串文本",
                },
            },
            "required": ["text"]
        }
    }
}
def reverse_string(text: str):
    if len(text) < 1:
        return f"请输入字符串"
    return text[::-1]