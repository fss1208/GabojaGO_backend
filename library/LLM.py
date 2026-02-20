# pip install openai langchain langchain-openai pydantic

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
import logging
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class CategoryModel(BaseModel):
    category: Literal["F", "T", "L", "E"] = Field(..., description="예산에 사용된 카테고리 4가지(F:식비, T:교통비, L:숙박비, E:기타)중 하나")

class TripGPT:

    def __init__(self, model_name: str):
        self._llm = ChatOpenAI(
            model = model_name,
            temperature = 0
        )

class CategoryGPT(TripGPT):

    def __init__(self):
        LLM_MODEL_CATEGORY = os.getenv("LLM_MODEL_CATEGORY")
        super().__init__(LLM_MODEL_CATEGORY)
        output_parser = PydanticOutputParser(pydantic_object=CategoryModel)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "너는 카카오 지도 API에서 받은 장소 정보를 기반으로 예산 카테고리를 분류하는 AI다. "
             "반드시 다음 4가지 중 하나만 선택하라: "
             "F:식비, T:교통비, L:숙박비, E:기타. "
             "기타는 숙박비, 식비, 교통비를 제외한 나머지 분류이다. "
             "다른 설명은 하지 말고 JSON 형식으로만 답하라. "
             ),
            ("system", "{format_instructions}"),
            ("human", 
             "다음은 카카오 지도 API에서 받은 장소 정보이다.\n\n"
             "place_name: {place_name}\n"
             "category_group_name: {category_group_name}\n"
             "category_name: {category_name}\n\n"
             "이 장소를 예산 카테고리로 분류하라."
             )
        ]).partial(format_instructions=output_parser.get_format_instructions())
        self.chain = prompt | self._llm | output_parser

if (__name__ == "__main__"):
    pass