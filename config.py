from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    database_url: str = "postgresql+asyncpg://prorobota:prorobota@postgres:5432/prorobota"
    redis_url: str = "redis://redis:6379/0"
    admin_ids: str = ""
    google_sheets_enabled: bool = False
    google_service_account_file: str = "/app/google_credentials/google-service-account.json"
    google_spreadsheet_id: str = ""
    google_worksheet_name: str = "Лиды"
    google_calendar_enabled: bool = False
    google_calendar_id: str = ""
    google_calendar_timezone: str = "Europe/Moscow"
    appointment_duration_minutes: int = 60
    appointment_step_minutes: int = 60
    appointment_min_hours_before: int = 4
    appointment_days_ahead: int = 14
    appointment_work_start: str = "10:00"
    appointment_work_end: str = "19:00"
    reminder_hours: str = "24,1"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    @property
    def admin_id_list(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_ids.split(",") if x.strip()}
    @property
    def reminder_hours_list(self) -> list[int]:
        return [int(x.strip()) for x in self.reminder_hours.split(",") if x.strip()]

@lru_cache
def get_settings(): return Settings()
settings=get_settings()
