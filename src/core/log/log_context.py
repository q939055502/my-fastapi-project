"""
��־�����Ĺ���ģ��

�ṩ��־�����ĵ����úͻ�ȡ���ܣ����� Python ContextVar ʵ��
֧�����첽�������Զ�����������
"""

from contextvars import ContextVarfrom dataclasses import dataclass@dataclass
class LogContext:
    """��־�����Ķ���

    ���ڴ洢������ص���������Ϣ��ʹ��־�ܹ�׷��������·

    Attributes:
        request_id: ����׷��ID
        tenant_id: �⻧ID
        user_id: �û�ID
        ip: �ͻ���IP��ַ
        endpoint: ����ӿ�·��
        duration: �����ʱ
        business_code: ҵ��״̬��
    """
    request_id: str = "-"
    tenant_id: str = "0"
    user_id: str = "0"
    ip: str = "unknown"
    endpoint: str = "-"
    duration: str = "0ms"
    business_code: str = "-"


# ContextVar ���� - �Զ�Э�̸���
CTX_LOG: ContextVar[LogContext] = ContextVar("log_context")


def set_log_context(context: LogContext) -> None:
    """���õ�ǰЭ�̵���־������

    Args:
        context: ��־�����Ķ���
    """
    CTX_LOG.set(context)


def get_log_context() -> LogContext:
    """��ȡ��ǰЭ�̵���־������

    Returns:
        LogContext: ��ǰ��־�����ģ�Ĭ��Ϊ��������
    """
    return CTX_LOG.get(LogContext())


def clear_log_context() -> None:
    """�����־������"""
    CTX_LOG.set(LogContext())


def create_log_context(
    request_id: str = "-",
    tenant_id: int | None = None,
    user_id: int | None = None,
    ip: str = "unknown",
    endpoint: str = "-",
    duration: str = "0ms",
    business_code: str = "-",
) -> LogContext:
    """��ݺ�����������־������

    Args:
        request_id: ����׷��ID
        tenant_id: �⻧ID����������תΪ�ַ�����
        user_id: �û�ID����������תΪ�ַ�����
        ip: �ͻ���IP��ַ
        endpoint: ����ӿ�·��
        duration: �����ʱ
        business_code: ҵ��״̬��

    Returns:
        LogContext: ��־�����Ķ���
    """
    return LogContext(
        request_id=request_id,
        tenant_id=str(tenant_id) if tenant_id else "system",
        user_id=str(user_id) if user_id else "0",
        ip=ip,
        endpoint=endpoint,
        duration=duration,
        business_code=business_code,
    )
