from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_user_table import ScheduleUserTable
from models.schedule_model import ScheduleUserModel, ScheduleUserListModel
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

@router.post("/append", summary="일정 동행자 추가", response_model=ScheduleUserModel)
def append_schedule_user(schedule_user_model: ScheduleUserModel, request: Request):
    """
    사용자가 요청하는 동행자를 일정에 추가
    - **ScheduleUserModel.iSchedulePK: int** 필수 입력
    - **ScheduleUserModel.iUserPK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_user_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_SELECT_DUPLICATED_USER_QUERY(schedule_user_model))
            if (result != 0):
                msg = f"{text_log} 실패! (이미 등록된 사용자, {schedule_user_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_INSERT_QUERY(schedule_user_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 등록 실패, {schedule_user_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_user_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_user_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_user_model

@router.post("/remove", summary="일정 동행자 삭제", response_model=dict)
def remove_schedule_user(iScheduleUserPK: int, request: Request):
    """
    사용자가 요청하는 동행자를 일정에서 삭제
    - **iScheduleUserPK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    request_log = f"iScheduleUserPK:{iScheduleUserPK}"
    logger.info(f"{text_log} 요청 ({request_log})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_DELETE_QUERY(iScheduleUserPK))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 삭제 실패, {request_log})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({request_log}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return {"iScheduleUserPK": iScheduleUserPK}

@router.get("/list", summary="동행자 목록 조회", response_model=ScheduleUserListModel)
def list_schedule(iSchedulePK: int, request: Request):
    """
    사용자가 요청하는 일정에 등록된 동행자 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(f"{text_log} 요청 ({request_log})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuples = cursor.fetchall()
            if (result != len(rows_tuples)):
                msg = f"{text_log} 실패! (데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuples)})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_user_list_model = ScheduleUserListModel(user_list=ScheduleUserTable.TO_MODEL_LIST(rows_tuples))
    logger.info(f"{text_log} 완료 ({request_log}:{result}개, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_user_list_model
