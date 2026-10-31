import ast
import operator

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _eval_ast(node: ast.AST) -> float:
    if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)):
        return node.value
    if isinstance(node,ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        return op(_eval_ast(node.left),_eval_ast(node.right))
    if isinstance(node,ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_eval_ast(node.operand))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")

def run(expression: str) -> str:
    """安全计算器：只支持 + - * / // % ** 和括号。"""
    expression = expression.strip()
    if not expression:
        return "ERROR: empty expression"
    try:
        tree = ast.parse(expression, mode="eval")
        # print(ast.dump(tree))
        return str(_eval_ast(tree.body))
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print(run("233*233"))

if __name__ == "__main__":
    main()
