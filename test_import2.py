#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

print("Testing imports step by step...")

try:
    print("1. Testing src.core.config import...")
    from src.core.config import settings
    print("   ✓ src.core.config imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("2. Testing src.core.storage.database import...")
    from src.core.storage.database import SessionLocal
    print("   ✓ src.core.storage.database imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("3. Testing src.core.storage.transaction_manager import...")
    from src.core.storage.transaction_manager import TransactionManager
    print("   ✓ src.core.storage.transaction_manager imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\nAll imports successful!")
