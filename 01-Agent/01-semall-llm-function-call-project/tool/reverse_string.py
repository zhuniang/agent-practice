"""Tool: reverse_string — 将输入字符串反转后返回。"""

def reverse_string(s: str):
    return s[::-1]

SCHEMA={
    "type": "function",
    "function": {
        "name": "reverse_string",
        "description": "这是一个反转字符串的工具，请在用户需要反转字符串时使用，如：帮我反转'abcd'、'qwrwe'的反转字符串是什么？",
        "parameters": {
            "type": "object",
            "properties": {
                "s": {
                    "type": "string",
                    "description": "输入的字符串，如'abcdef'"
                }
            },
            "required": ["s"]
        }
    }
}
