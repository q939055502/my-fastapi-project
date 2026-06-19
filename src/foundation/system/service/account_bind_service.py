"""
Account bind service - handle phone/email binding business logic
"""
from typing import Any

from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage import TransactionManager
from src.foundation.system.repository.account_bind_repository import (
    account_bind_repository,
)
from src.foundation.system.schemas.account_bind import (
    AccountBindCreate,
    AccountBindResponse,
)


class AccountBindService:

    def get_user_bindings(self, user_id: int) -> list[AccountBindResponse]:
        """Get all user bindings"""
        with TransactionManager() as tm:
            bindings = account_bind_repository.get_user_bindings(
                user_id=user_id,
                session=tm.session
            )
            return [AccountBindResponse.from_model(b) for b in bindings]

    def create_bind(self, user_id: int, bind_data: AccountBindCreate) -> AccountBindResponse:
        """Create new bind"""
        with TransactionManager() as tm:
            user_existing = account_bind_repository.get_by_user_and_type(
                user_id=user_id,
                bind_type=bind_data.bind_type,
                session=tm.session
            )
            if user_existing and bind_data.is_default:
                account_bind_repository.set_default(
                    user_id=user_id,
                    bind_id=0,
                    session=tm.session
                )

            new_bind = account_bind_repository.create_bind(
                user_id=user_id,
                bind_type=bind_data.bind_type,
                identifier=bind_data.identifier,
                is_default=bind_data.is_default,
                status="pending",
                source="manual",
                session=tm.session
            )
            tm.commit()

            logger.info(f"User created bind: user_id={user_id}, bind_type={bind_data.bind_type}")
            return AccountBindResponse.from_model(new_bind)

    def set_default_bind(self, user_id: int, bind_id: int) -> AccountBindResponse:
        """Set default bind"""
        with TransactionManager() as tm:
            bind = account_bind_repository.set_default(
                user_id=user_id,
                bind_id=bind_id,
                session=tm.session
            )
            if not bind:
                raise BusinessException(
                    40401,
                    "Bind not found"
                )
            tm.commit()
            logger.info(f"User set default bind: user_id={user_id}, bind_id={bind_id}")
            return AccountBindResponse.from_model(bind)

    def verify_bind(self, user_id: int, bind_id: int, code: str) -> AccountBindResponse:
        """Verify bind"""
        with TransactionManager() as tm:
            bind = account_bind_repository.verify_bind(
                user_id=user_id,
                bind_id=bind_id,
                session=tm.session
            )
            if not bind:
                raise BusinessException(
                    40401,
                    "Bind not found"
                )
            tm.commit()
            logger.info(f"User verified bind: user_id={user_id}, bind_id={bind_id}")
            return AccountBindResponse.from_model(bind)

    def disable_bind(self, user_id: int, bind_id: int) -> AccountBindResponse:
        """Disable bind"""
        with TransactionManager() as tm:
            bind = account_bind_repository.disable_bind(
                user_id=user_id,
                bind_id=bind_id,
                session=tm.session
            )
            if not bind:
                raise BusinessException(
                    40401,
                    "Bind not found"
                )
            tm.commit()
            logger.info(f"User disabled bind: user_id={user_id}, bind_id={bind_id}")
            return AccountBindResponse.from_model(bind)

    def delete_bind(self, user_id: int, bind_id: int) -> bool:
        """Delete bind"""
        with TransactionManager() as tm:
            success = account_bind_repository.delete_bind(
                user_id=user_id,
                bind_id=bind_id,
                session=tm.session
            )
            if not success:
                raise BusinessException(
                    40401,
                    "Bind not found"
                )
            tm.commit()
            logger.info(f"User deleted bind: user_id={user_id}, bind_id={bind_id}")
            return True

    def send_verification_code(self, user_id: int, bind_id: int) -> dict[str, Any]:
        """Send verification code (placeholder)"""
        with TransactionManager() as tm:
            bind = account_bind_repository.get(id=bind_id, session=tm.session)
            if not bind or bind.user_id != user_id:
                raise BusinessException(
                    40401,
                    "Bind not found"
                )

        logger.info(f"User requested verification code: user_id={user_id}, bind_id={bind_id}")

        return {
            "message": "Verification code sending pending",
            "bind_type": bind.bind_type,
            "identifier": bind.identifier
        }


account_bind_service = AccountBindService()
