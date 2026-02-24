from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_user_table import ScheduleUserTable
from models.schedule_model import ScheduleUserModel
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

@router.post("/register", summary="일정 참여자 등록", response_model=ScheduleUserModel)
def register_schedule_user(schedule_user_model: ScheduleUserModel):
    """
    여행 일정 참여자 등록
    """
    dt = datetime.now()
    logger.info(f"일정 참여자 등록 요청 ({schedule_user_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_INSERT_QUERY(schedule_user_model))
            if (result != 1):
                msg = f"일정 참여자 등록 실패! (DB 등록 실패, {schedule_user_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_user_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"일정 참여자 등록 완료 ({schedule_user_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_user_model

@router.post("/unregister", summary="일정 참여자 삭제", response_model=ScheduleUserModel)
def unregister_schedule_user(schedule_user_model: ScheduleUserModel):
    """
    여행 일정 참여자 삭제
    """
    dt = datetime.now()
    logger.info(f"일정 참여자 삭제 요청 ({schedule_user_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_DELETE_QUERY(schedule_user_model))
            if (result != 1):
                msg = f"일정 참여자 삭제 실패! (DB 삭제 실패, {schedule_user_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"일정 참여자 삭제 완료 ({schedule_user_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_user_model
