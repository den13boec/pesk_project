from fastapi import APIRouter, Depends
from ..auth.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/content/public")
def public_content(payload=Depends(get_current_user)):
    return {"message": f"Hello, {payload['sub']}! You have access to public content."}

@router.get("/content/private")
def private_content(payload=Depends(require_role("admin"))):
    return {"message": f"Hello, {payload['sub']}! You have access to admin-only content."}
