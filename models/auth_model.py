from pydantic import BaseModel, Field
from typing import Optional

class LoginRequestModel(BaseModel):
    strUserID: str = Field(..., min_length=3, max_length=255, example="KSH")
    strUserPW: str = Field(..., min_length=3, max_length=255, example="123")

class LoginResponseModel(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    token_type: str = Field(..., example="bearer")

class UserModel(BaseModel):
    iPK: Optional[int] = Field(0, example="0")
    strUserID: str = Field(..., example="KSH")
    strUserPW: str = Field(..., example="123")
    strName: str = Field(..., example="김성호")
    strEmail: str = Field(..., example="KSH@gmail.com")
    strPhone: Optional[str] = Field(None, example="010-1234-5678")
    strAddress: Optional[str] = Field(None, example="서울특별시 도봉구")
    strImageFile: Optional[str] = Field(None, example="/profile/ksh.jpg")

    def check_validation(self):
        # if (self.id is None or self.pw is None or self.name is None or self.email is None or self.phone is None or self.address is None):
        #     return False
        return True

    def to_log(self) -> str:
        return f"{self.iPK}:{self.strUserID}:{self.strName}"
