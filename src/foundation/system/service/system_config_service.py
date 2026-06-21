from sqlalchemy import asc, select

from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.system_config_repository import (
    system_config_repository,
)
from src.foundation.system.schemas.system_config import SystemConfigUpdate
from src.models.platform import SystemConfig


class SystemConfigService:
    def __init__(self):
        self.repository = system_config_repository

    def get_all_configs(self) -> dict:
        with TransactionManager() as tm:
            query = select(SystemConfig)
            query = self.repository._apply_soft_delete_filter(query)
            query = query.order_by(asc(SystemConfig.sort), asc(SystemConfig.id))
            result = tm.session.execute(query)
            config_objs = result.scalars().all()

            configs = {}
            for config in config_objs:
                configs[config.code] = {
                    "id": config.id,
                    "name": config.name,
                    "code": config.code,
                    "value": config.value,
                    "type": config.type,
                    "group": config.group,
                }

            return configs

    def update_configs(self, config_update: SystemConfigUpdate) -> None:
        with TransactionManager() as tm:
            for code, value in config_update.configs.items():
                config_obj = system_config_repository.get_by_code(code, session=tm.session)
                if not config_obj:
                    raise BusinessException(40401, detail=f"配置项不存在: {code}")

                config_obj.value = value

            tm.commit()


system_config_service = SystemConfigService()
