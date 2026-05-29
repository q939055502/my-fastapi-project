# Handlers 目录说明

本目录包含系统的各种处理器类，主要用于处理异步事件流、数据转换和内容安全过滤。

## 文件结构

```
handlers/
├── __init__.py              # 模块初始化
├── data_processor.py        # LLM流式响应数据处理器
├── sensitive_filter.py      # 敏感词过滤器
└── README.md               # 本文件
```

## 模块说明

### 1. DataProcessor (`data_processor.py`)

**功能**：处理 LLM (大语言模型) 返回的 Server-Sent Events (SSE) 流式响应数据。

**核心方法**：

| 方法 | 说明 |
|------|------|
| `extract_workflow_data(chunks)` | 从数据块中提取 `workflow_finished` 事件（AI 回答完成标记） |
| `extract_text_from_chunks(chunks)` | 累积合并所有文本块，获取完整回答内容 |
| `parse_chunk_event(chunk)` | 解析单个数据块中的事件 |
| `generate_title(query, answer)` | 根据提问和回答自动生成对话标题 |

**使用场景**：
- AI 聊天接口中解析流式响应
- 从多个数据块中提取完整回答
- 自动生成对话记录标题

---

### 2. SensitiveFilterHandler (`sensitive_filter.py`)

**功能**：统一的敏感词检测和过滤处理器，确保内容安全合规。

**核心方法**：

| 方法 | 说明 |
|------|------|
| `check_input(text)` | 检查输入文本是否包含敏感词 |
| `handle_sensitive_input_stream()` | 处理流式请求中的敏感内容 |
| `handle_sensitive_input_sync()` | 处理同步请求中的敏感内容 |
| `filter_chunk(chunk)` | 过滤数据块中的敏感词 |

**使用场景**：
- 用户输入内容审核（前置检查）
- AI 返回内容过滤（后置检查）
- 流式响应中的敏感内容拦截

---

## 典型工作流程

```
用户请求
    ↓
[敏感词检测] → 敏感内容 → 返回错误提示
    ↓ 正常
调用 LLM API
    ↓
[流式响应] → DataProcessor 解析 → SensitiveFilter 过滤 → 返回给用户
```

## 设计原则

1. **单一职责**：每个处理器只负责一类功能
2. **可复用性**：提供静态方法或单例实例，便于多处调用
3. **错误处理**：内置异常处理，确保系统稳定性
4. **日志记录**：关键操作记录日志，便于问题排查