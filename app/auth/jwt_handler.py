from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .jwt_service import JWTService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_data = JWTService.verify_token(token)
        return user_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
