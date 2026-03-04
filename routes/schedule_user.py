from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.user_table import UserTable
from database.schedule_table import ScheduleTable
from database.schedule.schedule_user_table import ScheduleUserTable
from models.schedule_model import ScheduleUserModel
from models.auth_model import UserListModel

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
def append_schedule_user(schedule_user_model: ScheduleUserModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 동행자를 일정에 추가
    - **ScheduleUserModel.iSchedulePK: int** 필수 입력
    - **ScheduleUserModel.iUserPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_user_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            # 스케줄을 생성한 사용자는 동행자에 포함시킬 수 없음
            result = DB.EXECUTE(cursor, ScheduleTable.TO_SELECT_CREATE_USER_QUERY(schedule_user_model.iScheduleFK, schedule_user_model.iUserFK))
            if (result != 0):
                connection.rollback()
                msg = f"스케줄을 생성한 사용자는 동행자에 포함 불가, {schedule_user_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            # 이미 일정에 등록된 사용자는 동행자에 포함시킬 수 없음
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_SELECT_DUPLICATED_USER_QUERY(schedule_user_model))
            if (result != 0):
                connection.rollback()
                msg = f"이미 일정에 등록된 사용자, {schedule_user_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            # 동행자 추가
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_INSERT_QUERY(schedule_user_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, result:{result}, {schedule_user_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_user_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_user_model.to_log(), dt))
    return schedule_user_model

@router.post("/remove", summary="일정 동행자 삭제", response_model=dict)
def remove_schedule_user(iScheduleUserPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 동행자를 일정에서 삭제
    - **iScheduleUserPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iScheduleUserPK:{iScheduleUserPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleUserTable.TO_DELETE_QUERY(iScheduleUserPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "에러", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iScheduleUserPK": iScheduleUserPK}

@router.get("/list", summary="동행자 목록 조회", response_model=UserListModel)
def list_schedule(iSchedulePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 동행자 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, UserTable.TO_SELECT_SUB_QUERY(ScheduleUserTable.TO_SELECT_USER_QUERY(iSchedulePK)))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "에러", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            user_list_model = UserListModel(user_list=UserTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return user_list_model
