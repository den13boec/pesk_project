from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from .. import schemas
from ..database import get_db
from ..users.crud import get_user_by_username
from .jwt import create_access_token, create_refresh_token, decode_token
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
r = Redis(host="redis", port=6379, decode_responses=True)

@router.post("/login")
async def login(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    # pylance is dumb, ignore error
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_data = {"sub": db_user.username, "role": db_user.role}
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    r.sadd("whitelist", access_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str):
    r.srem("whitelist", token)
    r.sadd("blacklist", token)
    return {"msg": "Logged out"}

@router.post("/refresh")
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access = create_access_token({"sub": payload["sub"], "role": payload["role"]})
    r.sadd("whitelist", new_access)
    return {"access_token": new_access}
