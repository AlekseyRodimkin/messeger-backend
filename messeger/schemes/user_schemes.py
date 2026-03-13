from pydantic import BaseModel, constr


class UserCreateScheme(BaseModel):
    username: str
    password: constr(min_length=10, max_length=72)


class ProfileScheme(BaseModel):
    username: str
