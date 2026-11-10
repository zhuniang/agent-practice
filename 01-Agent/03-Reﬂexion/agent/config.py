"""配置文件，加载env环境变量"""
from pathlib import Path
def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        root = Path(__file__).resolve().parents[3]
        load_dotenv(root/".env")
    except Exception as e:
        print(f"环境变量加载失败！")