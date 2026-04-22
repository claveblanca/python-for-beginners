# config.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()   # reads .env if it exists; silently ignored in production

MODEL_NAME  = os.getenv("MODEL_NAME",  "microsoft/DialoGPT-medium")
SERVER_PORT = int(os.getenv("SERVER_PORT", 7860))
LOG_LEVEL   = os.getenv("LOG_LEVEL",   "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
