# settings.py
from __future__ import annotations
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    base_url: str = os.getenv("BASE_URL")
    api_schema_url: str | None = os.getenv("API_SCHEMA_URL")
    login_path: str = os.getenv("LOGIN_PATH", "/auth/login/")
    register_path: str = os.getenv("REGISTER_PATH", "/auth/register/")
    blogs_path: str = os.getenv("BLOGS_PATH", "/blog/")
    comments_path: str = os.getenv("COMMENTS_PATH", "/comments/")
    likes_path: str = os.getenv("LIKES_PATH", "/likes/")
    shares_path: str = os.getenv("SHARES_PATH", "/shares/")

    username: str | None = os.getenv("API_USERNAME")
    password: str | None = os.getenv("API_PASSWORD")


SETTINGS = Settings()
