from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis import Redis
from .jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
r = Redis(host="redis", port=6379, decode_responses=True)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if r.sismember("blacklist", token):
        raise HTTPException(status_code=401, detail="Token is blacklisted")

    if not r.sismember("whitelist", token):
        raise HTTPException(status_code=401, detail="Token is not whitelisted")

    return payload

def require_role(required_role: str):
    async def role_checker(payload=Depends(get_current_user)):
        if payload.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return payload
    return role_checker
