from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.location_model import LocationModel, KakaoMapSearchRequestModel
from library.LLM import CategoryGPT
from library.MAP import KakaoMAP
from library.JWT import AuthJWT
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

@router.post("/search/keyword", summary="키워드로 장소 찾기", response_model=dict[str, LocationModel])
def search_keyword_kakaomap(request: Request, search_param: KakaoMapSearchRequestModel):
    """
    사용자가 요청하는 키워드에 해당하는 장소를 찾아 반환 (최대 15개)
    - **query**: 필수 입력
    """
    dt = datetime.now()
    logger.info(f"{request.url.path} 요청 수신 ({search_param})")
    location_dict = KakaoMAP.search_keyword(search_param)
    logger.info(f"{request.url.path} 처리 완료 ({LOG.TO_ESTIMATED_TIME(dt)})")
    return location_dict

@router.post("/register", summary="장소 등록")
def register_location(location_model: LocationModel):
    """
    사용자가 요청하는 장소를 등록 (장소 찾기로 전달한 정보 그대로 사용)
    """
    dt = datetime.now()
    logger.info(f"장소 등록 요청 ({location_model.id} {location_model.name})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationModel.SELECT_ID_QUERY(location_model.id))
            if (result != 0):
                msg = f"장소 등록 실패! (이미 등록된 장소 : {location_model.id} {location_model.name})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            result = DB.EXECUTE(cursor, location_model.insert_query())
            connection.commit()
            if (result != 1):
                msg = f"장소 등록 실패! (DB 등록 실패 : {location_model.id} {location_model.name})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            location_model.pk = cursor.lastrowid
    logger.info(f"장소 등록 완료 ({location_model.pk}:{location_model.name}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return {"message": f"등록 완료 ({location_model.pk}:{location_model.name})"}
 