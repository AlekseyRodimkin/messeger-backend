from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import validates
from passlib.context import CryptContext

from messeger.config import Base

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True, nullable=False
    )
    password_hash: so.Mapped[str] = so.mapped_column(
        sa.String(256), nullable=False
    )
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
        nullable=False
    )
    token_version: so.Mapped[int] = so.mapped_column(
        sa.Integer,
        default=0,
        nullable=False
    )

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 1:
            raise ValueError("Username must be at least 1 characters long")
        return username

    # password
    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def change_password(self, new_password: str):
        self.password_hash = pwd_context.hash(new_password)
        self.revoke_tokens()

    # username
    def change_username(self, new_username: str):
        self.username = new_username

    # token control
    def revoke_tokens(self):
        """Инвалидирует все refresh токены пользователя"""
        self.token_version += 1
