import ast
import operator
_BUINOP_MAP={
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UnaryOp_MAP={
    ast.UAdd: operator.pos, ast.USub: operator.neg
}

def _eval_expression(node: ast.AST):
    if isinstance(node,ast.Constant) and isinstance(node.value,(int, float)):
        return node.value
    if isinstance(node,ast.BinOp):
        return _BUINOP_MAP.get(type(node.op))(_eval_expression(node.left),_eval_expression(node.right))
    if isinstance(node,ast.UnaryOp):
        return _UnaryOp_MAP(type(node.op))(_eval_expression(node.operand))
    return f"输入了错误表达式"
def run(expression: str):
    """安全计算器：只支持 + - * / // % ** 和括号。"""
    expression = expression.strip()
    if not expression:
        return "ERROR: empty expression"
    try:
        tree = ast.parse(expression, mode="eval")
        # print(ast.dump(tree))
        return str(_eval_expression(tree.body))
    except Exception as e:
        return f"ERROR: {e}"
    


if __name__ == "__main__":
    # print(run("233*233") == str(233*233))
    print(run("233*233"))