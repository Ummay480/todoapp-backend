from sqlmodel import select
from app.models.user import User
from .password_service import PasswordService
from .jwt_service import JWTService
from sqlmodel import Session


def signin_user(db: Session, email: str, password: str):
    # Find user by email
    statement = select(User).where(User.email == email)
    result = db.execute(statement)
    user = result.first()

    if not user:
        raise ValueError("Signin failed")

    # Verify password
    if not PasswordService.verify_password(password, user.hashed_password):
        raise ValueError("Signin failed")

    # Create JWT token
    token = JWTService.create_token({
        "id": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
    })

    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }
