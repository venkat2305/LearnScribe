from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timezone
from app.db.mongodb import get_database
from app.config import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class User(BaseModel):
    user_id: str
    username: str
    email: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Reusable dependency to validate and decode a JWT token, then return the user from the DB.
    Raises HTTP 401 if token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("email")
        exp_iso_string: float = payload.get("expiry")

        if email is None or exp_iso_string is None:
            raise credentials_exception
        # # Check token expiration
        # exp_datetime = datetime.fromisoformat(exp_iso_string)
        # if datetime.now(tz=timezone.utc) > exp_datetime:
        #     raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = get_database()
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        raise credentials_exception

    return User(
        user_id=str(user_doc["user_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
    )
