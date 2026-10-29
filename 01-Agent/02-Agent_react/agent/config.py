from pathlib import Path

def load_env() -> None:
    """从项目根目录加载 .env（若已安装 python-dotenv）"""
    try:
        from dotenv import load_dotenv
    except Exception as e:
        raise ModuleNotFoundError("没有安装python-dotenv")
    root = Path(__file__).resolve().parents[3]
    load_dotenv(root/".env")