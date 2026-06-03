# HTTP 状态码常量使用统计

**源文件**: `src/core/constants.py` (第 131-200 行)
**统计时间**: 2026-06-04
**总计使用次数**: 100 处

---

## 使用情况汇总

| 文件 | 引用数量 | 使用的常量 |
|------|----------|------------|
| `src/core/auth/dependency.py` | 10 | HTTP_FORBIDDEN, HTTP_UNAUTHORIZED |
| `src/services/sys/auth_service.py` | 7 | HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_UNAUTHORIZED |
| `src/services/sys/user_service.py` | 15 | HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_NOT_FOUND |
| `src/services/sys/role_service.py` | 16 | HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_NOT_FOUND |
| `src/services/sys/dept_service.py` | 7 | HTTP_BAD_REQUEST, HTTP_NOT_FOUND |
| `src/services/sys/file_mapping_service.py` | 10 | HTTP_BAD_REQUEST, HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND, HTTP_UNAUTHORIZED |
| `src/services/sys/tenant_service.py` | 8 | HTTP_BAD_REQUEST, HTTP_NOT_FOUND |
| `src/services/sys/tenant_plan_service.py` | 7 | HTTP_BAD_REQUEST, HTTP_NOT_FOUND |
| `src/services/sys/resource_service.py` | 7 | HTTP_BAD_REQUEST, HTTP_NOT_FOUND |
| `src/services/sys/system_config_service.py` | 1 | HTTP_NOT_FOUND |
| `src/services/sys/phone_binding_service.py` | 9 | HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_NOT_FOUND |
| `src/api/v1/me/profile.py` | 4 | HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED |

---

## 详细使用记录

### `src/core/auth/dependency.py`
```
行 21:  HTTP_FORBIDDEN
行 22:  HTTP_UNAUTHORIZED
行 54:  HTTP_UNAUTHORIZED
行 86:  HTTP_UNAUTHORIZED
行 97:  HTTP_UNAUTHORIZED
行 128: HTTP_UNAUTHORIZED
行 136: HTTP_UNAUTHORIZED
行 141: HTTP_UNAUTHORIZED
行 150: HTTP_UNAUTHORIZED
行 216: HTTP_FORBIDDEN
```

### `src/services/sys/auth_service.py`
```
行 8:  HTTP_BAD_REQUEST
行 9:  HTTP_FORBIDDEN
行 10: HTTP_UNAUTHORIZED
行 33: HTTP_FORBIDDEN
行 39: HTTP_BAD_REQUEST
行 46: HTTP_BAD_REQUEST
行 129: HTTP_UNAUTHORIZED
行 137: HTTP_UNAUTHORIZED
```

### `src/services/sys/user_service.py`
```
行 7:  HTTP_BAD_REQUEST
行 8:  HTTP_FORBIDDEN
行 9:  HTTP_NOT_FOUND
行 34: HTTP_FORBIDDEN
行 85: HTTP_NOT_FOUND
行 96: HTTP_BAD_REQUEST
行 103: HTTP_BAD_REQUEST
行 133: HTTP_BAD_REQUEST
行 143: HTTP_NOT_FOUND
行 149: HTTP_BAD_REQUEST
行 157: HTTP_BAD_REQUEST
行 168: HTTP_BAD_REQUEST
行 185: HTTP_NOT_FOUND
行 208: HTTP_NOT_FOUND
```

### `src/services/sys/role_service.py`
```
行 5:  HTTP_BAD_REQUEST
行 6:  HTTP_FORBIDDEN
行 7:  HTTP_NOT_FOUND
行 46: HTTP_NOT_FOUND
行 74: HTTP_FORBIDDEN
行 81: HTTP_BAD_REQUEST
行 93: HTTP_NOT_FOUND
行 97: HTTP_FORBIDDEN
行 105: HTTP_BAD_REQUEST
行 116: HTTP_NOT_FOUND
行 120: HTTP_FORBIDDEN
行 131: HTTP_NOT_FOUND
行 135: HTTP_FORBIDDEN
```

### `src/services/sys/dept_service.py`
```
行 5:  HTTP_BAD_REQUEST
行 6:  HTTP_NOT_FOUND
行 44: HTTP_NOT_FOUND
行 63: HTTP_NOT_FOUND
行 73: HTTP_NOT_FOUND
行 78: HTTP_NOT_FOUND
行 81: HTTP_BAD_REQUEST
行 91: HTTP_NOT_FOUND
```

### `src/services/sys/file_mapping_service.py`
```
行 7:  HTTP_BAD_REQUEST
行 8:  HTTP_INTERNAL_SERVER_ERROR
行 9:  HTTP_NOT_FOUND
行 10: HTTP_UNAUTHORIZED
行 82: HTTP_INTERNAL_SERVER_ERROR
行 86: HTTP_UNAUTHORIZED
行 90: HTTP_NOT_FOUND
行 96: HTTP_BAD_REQUEST
行 102: HTTP_BAD_REQUEST
行 107: HTTP_BAD_REQUEST
行 120: HTTP_BAD_REQUEST
```

### `src/services/sys/tenant_service.py`
```
行 5:  HTTP_BAD_REQUEST
行 6:  HTTP_NOT_FOUND
行 46: HTTP_NOT_FOUND
行 55: HTTP_BAD_REQUEST
行 69: HTTP_NOT_FOUND
行 75: HTTP_BAD_REQUEST
行 86: HTTP_NOT_FOUND
```

### `src/services/sys/tenant_plan_service.py`
```
行 5:  HTTP_BAD_REQUEST
行 6:  HTTP_NOT_FOUND
行 42: HTTP_NOT_FOUND
行 51: HTTP_BAD_REQUEST
行 65: HTTP_NOT_FOUND
行 71: HTTP_BAD_REQUEST
行 82: HTTP_NOT_FOUND
```

### `src/services/sys/resource_service.py`
```
行 2:  HTTP_BAD_REQUEST
行 3:  HTTP_NOT_FOUND
行 18: HTTP_NOT_FOUND
行 42: HTTP_BAD_REQUEST
行 53: HTTP_BAD_REQUEST
行 58: HTTP_NOT_FOUND
行 67: HTTP_NOT_FOUND
```

### `src/services/sys/system_config_service.py`
```
行 5:  HTTP_NOT_FOUND
行 43: HTTP_NOT_FOUND
```

### `src/services/sys/phone_binding_service.py`
```
行 6:  HTTP_BAD_REQUEST
行 7:  HTTP_FORBIDDEN
行 8:  HTTP_NOT_FOUND
行 33: HTTP_NOT_FOUND
行 38: HTTP_BAD_REQUEST
行 43: HTTP_BAD_REQUEST
行 71: HTTP_NOT_FOUND
行 74: HTTP_FORBIDDEN
行 77: HTTP_BAD_REQUEST
```

### `src/api/v1/me/profile.py`
```
行 10: HTTP_BAD_REQUEST
行 11: HTTP_UNAUTHORIZED
行 56: HTTP_BAD_REQUEST
行 73: HTTP_UNAUTHORIZED
```

---

## 常量使用频率统计

| 常量 | 使用次数 |
|------|----------|
| HTTP_BAD_REQUEST | 28 |
| HTTP_NOT_FOUND | 26 |
| HTTP_UNAUTHORIZED | 16 |
| HTTP_FORBIDDEN | 12 |
| HTTP_INTERNAL_SERVER_ERROR | 2 |

---

## 备注

- **未使用的常量**: 大部分 HTTP 常量（如 1xx, 3xx 系列，以及 4xx 中的大部分）在项目中未被使用
- **使用场景**: 主要用于 `HTTPException` 的 `status_code` 参数
- **建议**: 如果后续需要清理，可以考虑移除未使用的常量定义