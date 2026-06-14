"""检查表结构"""
from src.common.core.storage import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dict_data' ORDER BY ordinal_position"))
    print("dict_data 表的列顺序:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
