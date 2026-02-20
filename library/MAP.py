from models.location_model import KakaoMapSearchRequestModel
import requests
import logging
import os

logger = logging.getLogger(__name__)

class KakaoMAP:

    @staticmethod
    def search_keyword(search_param: KakaoMapSearchRequestModel):
        KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        model_dict = search_param.model_dump()
        logger.debug(f"BEFORE {model_dict}")
        params = {k: v for k, v in model_dict.items() if v is not None}
        logger.debug(f"AFTER {params}")
        response = requests.get(url, headers=headers, params=params)
        return response.json()
