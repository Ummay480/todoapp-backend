from sqlmodel import select
from app.models.user import User
from .password_service import PasswordService
from .jwt_service import JWTService
from sqlmodel import Session


def signup_user(db: Session, full_name: str, email: str, password: str):
    # Check if user already exists
    existing_user = db.execute(select(User).where(User.email == email)).first()
    if existing_user:
        # Do NOT leak info
        raise ValueError("Signup failed")

    # Hash the password
    hashed = PasswordService.hash_password(password)

    # Create new user
    user = User(
        name=full_name,
        email=email,
        hashed_password=hashed
    )

    # Add user to database
    db.add(user)
    db.commit()
    db.refresh(user)

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
