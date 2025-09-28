import asyncio
import logging
from pydantic_settings import BaseSettings
from pathlib import Path

DOWNLOAD_DIR = Path(__file__).parent.parent / "downloads"

class Settings(BaseSettings):
    app_name: str = "CNDT Solver API"
    log_level: str = "INFO"
    captcha_api_key: str = "7b9f8da0567baa599a7a9508817a4992"
    download_dir: str = str(DOWNLOAD_DIR)
    max_concurrent_solvers: int = 3

settings = Settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

CONCURRENCY_LIMITER = asyncio.Semaphore(settings.max_concurrent_solvers)