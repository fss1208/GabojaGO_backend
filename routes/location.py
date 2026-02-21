from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.location_model import LocationModel, KakaoMapSearchRequestModel
from library.LLM import CategoryGPT
from library.MAP import KakaoMAP
from library.JWT import AuthJWT

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
    logger.info(f"{request.url.path} 처리 완료 ({(datetime.now() - dt).total_seconds() * 1000:.2f} ms)")
    return location_dict
