from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.db.mongodb import get_database
from app.config import config
from bson import ObjectId


# JWT settings
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter()


# Models
class User(BaseModel):
    username: str
    email: str
    user_id: str


class UserIn(BaseModel):
    username: str
    email: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_email(db, email: str):
    return await db.users.find_one({"email": email})


async def authenticate_user(db, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user["hashed_password"]):
        return False

    # If the hash is outdated, rehash and update the database
    if pwd_context.needs_update(user["hashed_password"]):
        new_hashed_password = get_password_hash(password)
        await db.users.update_one(
            {"email": email},
            {"$set": {"hashed_password": new_hashed_password}}
        )

    return user


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"email": user["email"], "expiry": expire.isoformat()},
        SECRET_KEY,
        algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(user_in: UserIn):
    db = get_database()
    if await db.users.find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = get_password_hash(user_in.password)
        new_user = {
            "user_id": str(ObjectId()),
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": hashed_password
        }

        await db.users.insert_one(new_user)
        return {
            "username": user_in.username,
            "email": user_in.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed, {str(e)}")
