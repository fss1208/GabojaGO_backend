from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

from routes import auth
from routes import favorite
from routes import favorite_location
from routes import location
from routes import schedule
from routes import schedule_location
from routes import schedule_expense
from routes import schedule_image
from routes import schedule_preparation
from routes import schedule_user

load_dotenv(override=True)
log_level = getattr(logging, os.getenv("LOG_LEVEL"), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(levelname)s:\t[%(asctime)s %(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"  # 날짜 형식 지정
)
logger = logging.getLogger(__name__)
logger.debug("LOG_LEVEL 설정 ({})".format(logging.getLevelName(log_level)))
app = FastAPI(title="가보자GO", version="0.1.0", description="Backend API Specification")

# 1. 허용할 출처(Origin) 목록 정의
origins = [
    "http://localhost:3000",                    # React/Next.js 기본 포트
    "https://gaboja-go-frontend.vercel.app"     # 실제 운영 도메인
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# prefix: 모든 경로 앞에 '/auth'가 자동으로 붙음 (예: /auth/login)
# tags: '/docs' & '/redoc' 페이지에서 해당 그룹으로 묶어서 표시
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(favorite.router, prefix="/favorite", tags=["Favorite Management"])
app.include_router(favorite_location.router, prefix="/favorite/location", tags=["Favorite Location Management"])
app.include_router(location.router, prefix="/location", tags=["Location Management"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule Management"])
app.include_router(schedule_location.router, prefix="/schedule/location", tags=["Schedule Location Management"])
app.include_router(schedule_expense.router, prefix="/schedule/expense", tags=["Schedule Expense Management"])
app.include_router(schedule_image.router, prefix="/schedule/image", tags=["Schedule Image Management"])
app.include_router(schedule_preparation.router, prefix="/schedule/preparation", tags=["Schedule Preparation Management"])
app.include_router(schedule_user.router, prefix="/schedule/user", tags=["Schedule User Management"])

@app.get("/")
async def root():
    return {"message": "메인 페이지"}

if (__name__ == "__main__"):
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
