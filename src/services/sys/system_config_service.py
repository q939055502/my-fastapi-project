from fastapi.exceptions import HTTPException

from src.repositories.sys.system_config_repository import system_config_repository
from src.schemas.sys.system_config import SystemConfigUpdate
from src.models.sys.system_config import SystemConfig
from src.core.log import logger
from src.core.storage import UnitOfWork
from sqlalchemy import asc, select


class SystemConfigService:
    def __init__(self):
        self.repository = system_config_repository
        self.logger = logger

    def get_all_configs(self) -> dict:
        with UnitOfWork() as uow:
            query = select(SystemConfig)
            query = self.repository._apply_soft_delete_filter(query)
            query = query.order_by(asc(SystemConfig.sort), asc(SystemConfig.id))
            result = uow.session.execute(query)
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
        with UnitOfWork() as uow:
            for code, value in config_update.configs.items():
                config_obj = system_config_repository.get_by_code(code, session=uow.session)
                if not config_obj:
                    raise HTTPException(status_code=404, detail=f"配置项不存在: {code}")

                config_obj.value = value

            uow.commit()


system_config_service = SystemConfigService()
