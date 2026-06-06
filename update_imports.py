#!/usr/bin/env python3
"""
批量更新项目导入路径的脚本
"""
import os
import re

# 定义替换规则
REPLACEMENTS = [
    # Models 层
    (r'from src\.models\.iam', 'from src.models.platform'),
    (r'from src\.models\.system', 'from src.models.platform'),
    
    # Schemas 层
    (r'from src\.schemas\.iam', 'from src.modules.platform.schemas'),
    (r'from src\.schemas\.system', 'from src.modules.platform.schemas'),
    (r'from src\.schemas\.tenant', 'from src.modules.tenant.schemas'),
    (r'from src\.schemas\.auth', 'from src.modules.auth.schemas'),
    
    # Repositories 层
    (r'from src\.repositories\.iam', 'from src.modules.platform.repository'),
    (r'from src\.repositories\.system', 'from src.modules.platform.repository'),
    (r'from src\.repositories\.tenant', 'from src.modules.tenant.repository'),
    (r'from src\.repositories\.order', 'from src.modules.order.repository'),
    
    # Services 层
    (r'from src\.services\.iam', 'from src.modules.platform.service'),
    (r'from src\.services\.system', 'from src.modules.platform.service'),
    (r'from src\.services\.tenant', 'from src.modules.tenant.service'),
    (r'from src\.services\.auth', 'from src.modules.auth.service'),
]


def update_file(file_path):
    """更新单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            print(f"Skipping (encoding error): {file_path}")
            return False
    
    original_content = content
    
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        return True
    return False


def main():
    """主函数"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    print("Updating imports in src directory...")
    
    updated_count = 0
    
    # 处理 src 目录
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    updated_count += 1
    
    # 处理 tests 目录
    print("\nUpdating imports in tests directory...")
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}")


if __name__ == '__main__':
    main()
