from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_expense_table import ScheduleExpenseTable
from models.schedule_model import ScheduleExpenseModel, ScheduleExpenseListModel
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

@router.post("/append", summary="지출 정보 등록", response_model=ScheduleExpenseModel)
def append_expense(schedule_expense_model: ScheduleExpenseModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 지출을 일정에 등록
    - **ScheduleExpenseModel.iSchedulePK: int** 필수 입력
    - **ScheduleExpenseModel.nMoney: int** 필수 입력
    - **ScheduleExpenseModel.dtExpense: datetime** 필수 입력
    - **ScheduleExpenseModel.chCategory: str** 필수 입력
    - **ScheduleExpenseModel.strMemo: str** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_expense_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            schedule_expense_model.iUserFK = login_user.iPK
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_INSERT_QUERY(schedule_expense_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {schedule_expense_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_expense_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_expense_model.to_log(), dt))
    return schedule_expense_model

@router.post("/modify", summary="지출 정보 수정", response_model=ScheduleExpenseModel)
def modify_expense(schedule_expense_model: ScheduleExpenseModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 지출의 정보 수정
    - **ScheduleExpenseModel.iPK: int** 필수 입력
    - **ScheduleExpenseModel.nMoney: int** 수정 항목
    - **ScheduleExpenseModel.dtExpense: datetime** 수정 항목
    - **ScheduleExpenseModel.chCategory: str** 수정 항목
    - **ScheduleExpenseModel.strMemo: str** 수정 항목
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_expense_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_UPDATE_QUERY(schedule_expense_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 수정 실패, {schedule_expense_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_expense_model.to_log(), dt))
    return schedule_expense_model

@router.post("/remove", summary="지출 정보 삭제", response_model=dict)
def remove_expense(iScheduleExpensePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 지출 정보 삭제
    - **iScheduleExpensePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iScheduleExpensePK:{iScheduleExpensePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_DELETE_QUERY(iScheduleExpensePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iScheduleExpensePK": iScheduleExpensePK}

@router.get("/list", summary="지출 정보 조회", response_model=ScheduleExpenseListModel)
def list_expense(iSchedulePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 지출 정보 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_expense_list_model = ScheduleExpenseListModel(expense_list=ScheduleExpenseTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return schedule_expense_list_model
