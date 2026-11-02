"""配置文件"""
from pathlib import Path
def load_env():
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parents[3]
        load_dotenv(env_path/".env")
        
    except Exception as e:
        print(f"导入环境变量失败")

