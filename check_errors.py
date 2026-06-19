# -*- coding: utf-8 -*-
import os
import subprocess
import sys

errors = []
for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', path],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                errors.append(path)

print(f'Total: {len(errors)}')
for p in errors:
    print(p)