"""
�������

�ṩͳһ���������ܣ����� slowapi ʵ�֡�
"""

import osfrom slowapi import Limiterfrom slowapi.util import get_remote_addresslimiter = Limiter(key_func=get_remote_address)


def apply_rate_limit(rate: str = "5/minute"):
    """
    ����װ������������

    Args:
        rate: �������ʣ���ʽΪ "����/ʱ�䵥λ"
              ����: "5/minute", "10/second", "100/hour"

    Returns:
        װ�������������Ի����»���������
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return lambda func: func
    return limiter.limit(rate)
