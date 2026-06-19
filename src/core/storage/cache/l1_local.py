"""L1 �����ڴ滺��

ʵ�ֻ����ڴ�ı��ػ��棬��Ϊ Redis ��ǰ�˻���㣨L1 Cache����
֧�� LRU���������ʹ�ã��� TTL������ʱ�䣩���ԡ�
"""


import timefrom collections import OrderedDictfrom typing import Anyclass L1LocalCache:
    """L1 �����ڴ滺��ʵ��"""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300
    ):
        """
        ��ʼ�� L1 ���档

        Args:
            max_size: ���洢��Ŀ��
            default_ttl: Ĭ������ʱ�䣨�룩
        """
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """���ݼ���ȡֵ"""
        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]

        # ����Ƿ����
        if time.time() >= expire_time:
            del self._cache[key]
            return None

        # �����ʵļ��Ƶ�ĩβ��LRU ���ԣ�
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """����ֵ����ѡָ�� TTL

        ע�⣺���ﲻ�������ƫ�ƣ��ɻ��������ͳһ����

        Args:
            key: �����
            value: Ҫ�����ֵ
            ttl: ����ʱ�䣨�룩�����Ϊ None ��ʹ��Ĭ�� TTL
        """
        # ������Ѵ��ڣ���ɾ��
        if key in self._cache:
            del self._cache[key]

        # �������������ɾ�����δʹ�õ���Ŀ��LRU ���ԣ�
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        # �������ʱ��
        final_ttl = ttl if ttl is not None else self._default_ttl
        expire_time = time.time() + final_ttl
        self._cache[key] = (value, expire_time)

    def delete(self, key: str) -> None:
        """���ݼ�ɾ��ֵ"""
        if key in self._cache:
            del self._cache[key]

    def clear_pattern(self, pattern: str) -> None:
        """�������ƥ��ģʽ�ļ�"""
        keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

    def clear(self) -> None:
        """������л�����Ŀ"""
        self._cache.clear()

    def size(self) -> int:
        """��ȡ��ǰ�����С"""
        return len(self._cache)
