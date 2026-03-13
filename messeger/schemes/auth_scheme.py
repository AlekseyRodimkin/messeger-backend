from pydantic import BaseModel, constr


class LoginScheme(BaseModel):
    username: str
    password: str


class CorrectLoginResponseScheme(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequestScheme(BaseModel):
    refresh_token: str


class RefreshTokenResponseScheme(BaseModel):
    access_token: str
    refresh_token: str
