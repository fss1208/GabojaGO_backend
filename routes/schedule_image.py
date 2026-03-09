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

import shutil
from fastapi import File, UploadFile
from library.IMG import get_exif_location, debug_gps
from library.WEBP import convert_to_webp
from library.CF import CloudFlare

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

def CreateCloudFlare():
    account_id = os.getenv("CF_ACCOUNT_ID")
    access_key = os.getenv("CF_ACCESS_KEY")
    secret_key = os.getenv("CF_SECRET_KEY")
    bucket_name = os.getenv("CF_BUCKET_NAME")
    return CloudFlare(account_id, access_key, secret_key, bucket_name)

#################################################################################################################

@router.post("/append", summary="이미지 정보 추가", response_model=ScheduleImageFrontModel)
async def append_schedule_image(request: Request, iSchedulePK: int, iLocationPK: int, file: UploadFile = File(...), auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 업로드 요청하는 이미지 파일 정보 추가 : Cloudflare 업로드 및 Database 저장 (image, schedule_image)
    - **iSchedulePK: int** 필수 입력 (ScheduleTable.iPK > 0)
    - **iLocationPK: int** 필수 입력 (LocationTable.iPK >= 0)
    - **file: UploadFile** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"{iSchedulePK}:{iLocationPK}:{file.filename}:{file.content_type}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    # 1. 프론트가 업로드 요청한 파일 저장
    upload_path = f"uploads/{login_user.strUserID}"
    upload_file = f"{upload_path}/{file.filename}"
    os.makedirs(upload_path, exist_ok=True) # 폴더가 없으면 생성, 존재하면 그냥 넘어감 (exist_ok=True)
    files = [f for f in os.listdir(upload_path) if os.path.isfile(os.path.join(upload_path, f))]
    for previous_upload_file in files:
        os.remove(f"{upload_path}/{previous_upload_file}")
        logger.info(f"기존에 업로드된 파일 삭제 ({upload_path}/{previous_upload_file})")
    with open(upload_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"업로드 완료 ({upload_file})")
    # 2. 업로드된 파일에서 데이터 추출 (위도, 경도, 촬영일시)
    debug_gps(upload_file)
    img_extract_dict, error_msg = get_exif_location(upload_file)
    img_date_str = img_extract_dict.get("dt").split(" ")[0] if bool(img_extract_dict) and bool(img_extract_dict.get("dt")) else None
    if (img_date_str == None):
        msg = f"이미지 파일에서 촬영일시 추출 실패 ({error_msg})"
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)
    logger.info(f"이미지 파일로부터 데이터 추출 완료 ({img_extract_dict})")
    # 3. WebP 형식으로 파일 변환
    ext = os.path.splitext(file.filename)[1]
    webp_file = upload_file.replace(ext, ".webp")
    convert_to_webp(upload_file, webp_file, 10)
    logger.info(f"이미지 변환 완료 ({webp_file})")
    # 4. CloudFlare에 파일 업로드
    cf_upload_path = f"{img_date_str.replace("-", "/")}/{login_user.strUserID}"
    cf_upload_file = webp_file.replace(upload_path, cf_upload_path)
    cf = CreateCloudFlare()
    if not cf.upload_file(webp_file, cf_upload_file):
        msg = f"파일서버에 업로드 실패 ({webp_file} > {cf_upload_file})"
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)
    logger.info(f"파일서버에 업로드 완료 ({cf_upload_file})")
    # 5. database data 추가 (ImageTable, ScheduleImageTable)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ImageTable.TO_SELECT_FILE_QUERY(cf_upload_file))
            if (result != 0):
                msg = f"이미 존재하는 파일 ({cf_upload_file})"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            # ImageTable.INSERT
            image_model = ImageModel(
                iPK=0,
                iUserFK=login_user.iPK,
                iLocationPK=iLocationPK,
                strFile=cf_upload_file,
                dtImage=datetime.strptime(img_extract_dict.get("dt"), "%Y-%m-%d %H:%M:%S"),
                ptLongitude=str(img_extract_dict.get("x")) if img_extract_dict.get("x") else "0.0",
                ptLatitude=str(img_extract_dict.get("y")) if img_extract_dict.get("y") else "0.0",
                dtCreate=datetime.now()
            )
            result = DB.EXECUTE(cursor, ImageTable.TO_INSERT_QUERY(image_model))
            if (result != 1):
                connection.rollback()
                cf.delete_file(cf_upload_file)
                msg = f"ImageTable 이미지 등록 실패, {image_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            image_model.iPK = cursor.lastrowid
            # ScheduleImageTable.INSERT
            schedule_image_model = ScheduleImageFrontModel(iPK=0, iScheduleFK=iSchedulePK, iImageFK=image_model.iPK, image=image_model)
            result = DB.EXECUTE(cursor, ScheduleImageTable.TO_INSERT_QUERY(iSchedulePK, image_model.iPK))
            if (result != 1):
                connection.rollback()
                cf.delete_file(cf_upload_file)
                msg = f"ScheduleImageTable 일정 등록 실패, {schedule_image_model.to_log()}"
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
            # ImageTable 이미지 존재 여부 확인
            result = DB.EXECUTE(cursor, ImageTable.TO_SELECT_MODEL_QUERY(iImagePK))
            if (result != 1):
                msg = f"ImageTable 이미지 존재하지 않음, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            image_model = ImageTable.TO_MODEL(cursor.fetchone())
            # ScheduleImageTable 삭제
            result = DB.EXECUTE(cursor, ScheduleImageTable.TO_DELETE_QUERY(iScheduleImagePK))
            if (result != 1):
                connection.rollback()
                msg = f"ScheduleImageTable 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            # ImageTable 삭제
            result = DB.EXECUTE(cursor, ImageTable.TO_DELETE_QUERY(iImagePK))
            if (result != 1):
                connection.rollback()
                msg = f"ImageTable 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
            # 파일서버에 업로드된 파일 삭제
            cf = CreateCloudFlare()
            cf.delete_file(image_model.strFile)
            logger.info(f"파일서버에 업로드된 파일 삭제 완료 ({image_model.strFile})")
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
