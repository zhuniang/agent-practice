import re
pats = [r"字符数\s*[:：]\s*2\b", r"\b2\s*个字符", r"字符数.{0,20}2"]
outs = [
 "Final Answer: 21+21=42，字符串'42'的长度为2个字符",
 "Final Answer: 42，结果字符串长度为2个字符",
 "Final Answer: 42，字符数：2个字符",
 "Final Answer: 42，字符数：2",
 "Final Answer: 42 的字符数为 2",
 "Final Answer: 42（两个字符）",
 "Final Answer: 42，字符串长度为 2",
 "42，共2个字符",
 "答案：42；长度：2",
]
for o in outs:
    hits = [bool(re.search(p, o)) for p in pats]
    print(("PASS" if all(hits) else "FAIL"), hits, o)
