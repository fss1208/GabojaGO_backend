from fastapi import FastAPI
from dotenv import load_dotenv
import logging
import os

load_dotenv(override=True)
log_level = getattr(logging, os.getenv("LOG_LEVEL"), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s %(levelname)s %(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"  # 날짜 형식 지정
)
logger = logging.getLogger(__name__)
logger.debug("LOG_LEVEL 설정 ({})".format(logging.getLevelName(log_level)))
app = FastAPI(title="가보자GO", version="0.1.0", description="Backend API Specification")

@app.get("/")
async def root():
    return {"message": "메인 페이지"}