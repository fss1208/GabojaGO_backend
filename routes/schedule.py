from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule_table import ScheduleTable
from models.schedule_model import ScheduleModel
from library.JWT import AUTH_JWT
from library.LOG import LOG
from library.DB import DB

from datetime import datetime, timedelta
import logging
import json
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

#################################################################################################################

@router.post("/create", summary="일정 생성", response_model=ScheduleModel)
def create_schedule(schedule_model: ScheduleModel, request: Request):
    """
    사용자가 요청하는 일정을 생성
    - **ScheduleModel.iPK: int** 이 항목만 제외하고 나머지 항목 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleTable.TO_INSERT_QUERY(schedule_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 등록 실패, {schedule_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_model
