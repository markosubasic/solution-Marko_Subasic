import logging

from fastapi import APIRouter, HTTPException, status

from tickethub import dummyjson
from tickethub.auth import create_access_token
from tickethub.schemas import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await dummyjson.login(payload.username, payload.password)
    if user is None:
        logger.warning("Failed login attempt for user %s", payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return TokenResponse(access_token=create_access_token(payload.username))
