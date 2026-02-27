from pydantic import BaseModel, Field
from typing import Optional

class FavoriteModel(BaseModel):
    iPK: int = Field(..., example=0)
    iUserFK: int = Field(..., example=1)
    strName: str = Field(..., max_length=255, example="즐겨찾기 이름")

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iUserFK}:{self.strName}"

class FavoriteListModel(BaseModel):
    favorite_list: list[FavoriteModel] = Field(..., description="즐겨찾기 목록")
