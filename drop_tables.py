"""删除所有数据库表"""
from src.core.storage import Base, engine
from sqlalchemy import text, inspect

# 创建检查器对象
inspector = inspect(engine)

with engine.connect() as conn:
    # 获取当前数据库中的所有表名
    tables = inspector.get_table_names()
    
    print(f"找到 {len(tables)} 个表，开始删除...")
    
    for table in tables:
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            print(f'已删除表: {table}')
        except Exception as e:
            print(f'删除表 {table} 失败: {e}')
    
    conn.commit()

print('所有表已删除完成')
