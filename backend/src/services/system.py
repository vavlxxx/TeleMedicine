from src.schemas.system import MaintenanceStateDTO
from src.services.base import BaseService

APP_UNAVAILABLE_OPTION_CODE = "app_unavailable"


def _parse_bool_option(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class MaintenanceService(BaseService):
    async def get_state(self) -> MaintenanceStateDTO:
        state = await self.db.app_options.get_or_create(APP_UNAVAILABLE_OPTION_CODE, "false")
        await self.db.commit()
        return MaintenanceStateDTO(enabled=_parse_bool_option(state.value), updated_at=state.updated_at)

    async def update_state(self, enabled: bool) -> MaintenanceStateDTO:
        state = await self.db.app_options.get_or_create(APP_UNAVAILABLE_OPTION_CODE, "false")
        state.value = "true" if enabled else "false"
        await self.db.commit()
        await self.db.refresh(state)
        return MaintenanceStateDTO(enabled=_parse_bool_option(state.value), updated_at=state.updated_at)
