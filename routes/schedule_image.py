from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.image_table import ImageTable
from database.location_table import LocationTable
from database.schedule.schedule_image_view import ScheduleImageView
from database.schedule.schedule_image_table import ScheduleImageTable
from models.schedule_model import ScheduleImageModel, ScheduleImageFrontModel, ScheduleImageListModel
from models.image_model import ImageModel

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

@router.post("/append", summary="이미지 정보 추가", response_model=ScheduleImageFrontModel)
def append_schedule_image(iSchedulePK: int, image_model: ImageModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 이미지 정보 추가
    - **iSchedulePK: int** 필수 입력
    - **ImageModel.iPK: int** 기본값 (default = 0)
    - **ImageModel.iUserFK: int** 기본값 (default = 0)
    - **ImageModel.iLocationPK: int** 선택 입력 (default = 0)
    - **ImageModel.strFile: str** **필수 입력**
    - **ImageModel.dtImage: datetime** **필수 입력**
    - **ImageModel.ptLongitude: str** **필수 입력**
    - **ImageModel.ptLatitude: str** **필수 입력**
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", image_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            # ImageTable.INSERT
            image_model.iUserFK = login_user.iPK
            result = DB.EXECUTE(cursor, ImageTable.TO_INSERT_QUERY(image_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 이미지 등록 실패, {image_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            image_model.iPK = cursor.lastrowid
            # ScheduleImageTable.INSERT
            schedule_image_model = ScheduleImageFrontModel(iPK=0, iScheduleFK=iSchedulePK, iImageFK=image_model.iPK, image=image_model)
            result = DB.EXECUTE(cursor, ScheduleImageTable.TO_INSERT_QUERY(iSchedulePK, image_model.iPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 일정 등록 실패, {schedule_image_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_image_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_image_model.to_log(), dt))
    return schedule_image_model

@router.post("/remove", summary="이미지 정보 삭제", response_model=dict)
def remove_schedule_image(iScheduleImagePK: int, iImagePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 이미지 정보 삭제
    - **iScheduleImagePK: int** 필수 입력
    - **iImagePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iScheduleImagePK:{iScheduleImagePK},iImagePK:{iImagePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleImageTable.TO_DELETE_QUERY(iScheduleImagePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            result = DB.EXECUTE(cursor, ImageTable.TO_DELETE_QUERY(iImagePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iScheduleImagePK": iScheduleImagePK, "iImagePK": iImagePK}

@router.get("/list", summary="이미지 정보 조회", response_model=ScheduleImageListModel)
def list_schedule_image(iSchedulePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 이미지 정보 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleImageView.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_image_list_model = ScheduleImageListModel(image_list=ScheduleImageView.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return schedule_image_list_model
