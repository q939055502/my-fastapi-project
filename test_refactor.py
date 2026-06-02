#!/usr/bin/env python
"""测试重构后的代码"""

from src.core.storage.transaction_manager import TransactionManager
from src.core.storage.cache.cache_manager import cache_manager, clear_user_cache, clear_role_cache

print("Testing TransactionManager...")
tm = TransactionManager()
print("✓ TransactionManager imported successfully")

print("Testing cache_manager...")
print(f"✓ cache_manager imported successfully, enabled: {cache_manager.enabled}")

print("Testing convenience functions...")
print("✓ clear_user_cache and clear_role_cache imported successfully")

print("\n=== All imports successful! ===")
