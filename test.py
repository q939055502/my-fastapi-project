"""
缓存 TTL 配置文件
规则：
1. L1本地缓存 时长 < L2 Redis 缓存时长
2. 数据越稳定，缓存时长越长
3. 自带随机偏移量，防止缓存雪崩
"""

# ===================== 基础配置 =====================
# 是否开启缓存时长随机偏移（生产强烈建议开启，防雪崩）
CACHE_TTL_RANDOM_ENABLE = True
# 随机偏移范围（秒）：比如 300 = ±5分钟，避免所有缓存同一时间过期
CACHE_TTL_RANDOM_OFFSET = 300

# ===================== 缓存层级常量 =====================
class CacheLevel:
    L1_LOCAL = "l1_local"    # 本地缓存（Caffeine）
    L2_REDIS = "l2_redis"    # 分布式缓存（Redis）

# ===================== 分表、分层级 TTL 配置（核心！） =====================
# 单位：秒
# 0 = 不缓存
CACHE_TTL_SETTINGS = {
    # ==================== 【预热核心表】几乎不变的数据 ====================
    "sys_config": {  # 系统配置表（你的预热函数用这个）
        CacheLevel.L1_LOCAL: 5 * 60,      # 本地缓存：5分钟
        CacheLevel.L2_REDIS: 24 * 60 * 60  # Redis缓存：24小时
    },
    "sys_dict": {  # 数据字典表
        CacheLevel.L1_LOCAL: 5 * 60,
        CacheLevel.L2_REDIS: 24 * 60 * 60
    },
    "region": {  # 省市区表
        CacheLevel.L1_LOCAL: 10 * 60,
        CacheLevel.L2_REDIS: 7 * 24 * 60 * 60
    },

    # ==================== 低频更新数据 ====================
    "product": {  # 商品表
        CacheLevel.L1_LOCAL: 30,          # 本地缓存：30秒
        CacheLevel.L2_REDIS: 2 * 60 * 60  # Redis缓存：2小时
    },
    "user_info": {  # 用户基础信息
        CacheLevel.L1_LOCAL: 60,
        CacheLevel.L2_REDIS: 1 * 60 * 60
    },

    # ==================== 高频更新数据 ====================
    "product_stock": {  # 商品库存
        CacheLevel.L1_LOCAL: 5,
        CacheLevel.L2_REDIS: 60
    },

    # ==================== 强实时数据（不缓存） ====================
    "order": {  # 订单表
        CacheLevel.L1_LOCAL: 0,
        CacheLevel.L2_REDIS: 0
    },
    "user_wallet": {  # 用户余额
        CacheLevel.L1_LOCAL: 0,
        CacheLevel.L2_REDIS: 0
    }
}

# ===================== 工具函数（自动获取带偏移的缓存时长） =====================
import random

def get_cache_ttl(table_name: str, cache_level: str) -> int:
    """
    获取指定表、指定缓存层级的 TTL（自动处理随机偏移）
    :param table_name: 数据表名（如 sys_config、product）
    :param cache_level: 缓存层级（CacheLevel.L1_LOCAL / CacheLevel.L2_REDIS）
    :return: 最终缓存时长（秒）
    """
    # 1. 获取配置的基础时长
    base_ttl = CACHE_TTL_SETTINGS.get(table_name, {}).get(cache_level, 0)
    
    # 2. 不缓存 / 无需偏移
    if base_ttl == 0 or not CACHE_TTL_RANDOM_ENABLE:
        return base_ttl
    
    # 3. 添加随机偏移（防止缓存雪崩）
    offset = random.randint(-CACHE_TTL_RANDOM_OFFSET, CACHE_TTL_RANDOM_OFFSET)
    final_ttl = base_ttl + offset
    
    # 保证时长大于 0
    return max(final_ttl, 1)