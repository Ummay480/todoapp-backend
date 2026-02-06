from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import get_session
from app.auth.signup_service import signup_user
from app.auth.signin_service import signin_user
from sqlmodel import Session

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str


class SigninRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_session)):
    print(f"Signup endpoint called with: {payload}")
    try:
        result = signup_user(
            db,
            payload.full_name,
            payload.email,
            payload.password,
        )
        print(f"Signup successful: {result}")
        return result
    except ValueError as e:
        print(f"Signup ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Signup general error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Signup failed")


@router.post("/signin")
def signin(payload: SigninRequest, db: Session = Depends(get_session)):
    try:
        return signin_user(
            db,
            payload.email,
            payload.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Signin failed")
