import logging
import os
from logging.handlers import RotatingFileHandler
from ..config import BASE_DIR

LOG_FILE = os.path.join(BASE_DIR, "backend.log")

logger = logging.getLogger("ai_data_processing")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
