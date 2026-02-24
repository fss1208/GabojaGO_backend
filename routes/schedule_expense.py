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
def append_expense(schedule_expense_model: ScheduleExpenseModel, request: Request):
    """
    사용자가 요청하는 지출을 일정에 등록
    - **ScheduleExpenseModel.iSchedulePK: int** 필수 입력
    - **ScheduleExpenseModel.iUserPK: int** 필수 입력
    - **ScheduleExpenseModel.dtExpense: datetime** 필수 입력
    - **ScheduleExpenseModel.chCategory: str** 필수 입력
    - **ScheduleExpenseModel.nMoney: int** 필수 입력
    - **ScheduleExpenseModel.iLocation: int** 필수 입력
    - **ScheduleExpenseModel.strMemo: str** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_expense_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_INSERT_QUERY(schedule_expense_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 등록 실패, {schedule_expense_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_expense_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_expense_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_expense_model

@router.post("/modify", summary="지출 정보 수정", response_model=ScheduleExpenseModel)
def modify_expense(schedule_expense_model: ScheduleExpenseModel, request: Request):
    """
    사용자가 요청하는 일정에 등록된 지출의 정보 수정
    - **ScheduleExpenseModel.iPK: int** 필수 입력
    - **ScheduleExpenseModel.dtExpense: datetime** 수정 항목
    - **ScheduleExpenseModel.chCategory: str** 수정 항목
    - **ScheduleExpenseModel.nMoney: int** 수정 항목
    - **ScheduleExpenseModel.iLocation: int** 수정 항목
    - **ScheduleExpenseModel.strMemo: str** 수정 항목
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_expense_model.model_dump()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_UPDATE_QUERY(schedule_expense_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 수정 실패, {schedule_expense_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_expense_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_expense_model

@router.post("/remove", summary="지출 정보 삭제", response_model=ScheduleExpenseModel)
def remove_expense(schedule_expense_model: ScheduleExpenseModel, request: Request):
    """
    사용자가 요청하는 일정에 등록된 지출 정보 삭제
    - **ScheduleExpenseModel.iPK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_expense_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_DELETE_QUERY(schedule_expense_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 삭제 실패, {schedule_expense_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_expense_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_expense_model

@router.get("/list", summary="지출 정보 조회", response_model=ScheduleExpenseListModel)
def list_expense(iSchedulePK: int, request: Request):
    """
    사용자가 요청하는 일정에 등록된 지출 정보 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(f"{text_log} 요청 ({request_log})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleExpenseTable.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuples = cursor.fetchall()
            if (result != len(rows_tuples)):
                msg = f"{text_log} 실패! (데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuples)})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_expense_list_model = ScheduleExpenseListModel(expense_list=ScheduleExpenseTable.TO_MODEL_LIST(rows_tuples))
    logger.info(f"{text_log} 완료 ({request_log}:{result}개, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_expense_list_model
