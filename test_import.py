#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Testing imports...")

try:
    from src.core.storage.transaction_manager import TransactionManager
    print("✓ TransactionManager imported successfully")
except Exception as e:
    print(f"✗ Failed to import TransactionManager: {e}")
