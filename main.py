from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import logging
import os

from routes import auth
from routes import location

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

# prefix: 모든 경로 앞에 '/auth'가 자동으로 붙음 (예: /auth/login)
# tags: '/docs' & '/redoc' 페이지에서 해당 그룹으로 묶어서 표시
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(location.router, prefix="/location", tags=["Location Management"])

@app.get("/")
async def root():
    return {"message": "메인 페이지"}

if (__name__ == "__main__"):
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)