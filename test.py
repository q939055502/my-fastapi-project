import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# 日志根目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式（保持你原有的格式）
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --------------------------
# 核心：启用【按天轮转 + 自动保留7天】
# --------------------------
file_handler = TimedRotatingFileHandler(
    filename=LOG_DIR / "app.log",
    when="D",        # 按天切割
    interval=1,      # 1天一个文件
    backupCount=7,   # 只保留最近7天，自动删除老日志 ✅
    encoding="utf-8",
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 控制台输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 根日志配置
def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# 全局导出
logger = setup_logger()