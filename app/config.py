# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_URL = os.getenv("REDIS_URL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

settings = Settings()
