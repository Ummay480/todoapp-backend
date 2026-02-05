import jwt
import time
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Use Better Auth secret if available, fallback to JWT_SECRET, but ensure it's set in production
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", os.getenv("JWT_SECRET", "CHANGE_THIS_TO_ENV_SECRET"))

if JWT_SECRET == "CHANGE_THIS_TO_ENV_SECRET" and os.getenv("ENVIRONMENT") == "production":
    logger.error("WARNING: Using default JWT secret in production. This is insecure!")
    raise ValueError("JWT_SECRET environment variable is required in production")

JWT_ALGORITHM = "HS256"
# Token expiration: 24 hours in production, 1 hour in development
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", 24 * 60 * 60 if os.getenv("ENVIRONMENT") == "production" else 60 * 60))


class JWTService:
    @staticmethod
    def create_token(payload: Dict[str, Any]) -> str:
        now = int(time.time())
        token_payload = {
            **payload,
            "iat": now,
            "exp": now + JWT_EXPIRES_IN,
        }

        logger.info(f"Creating JWT token for user: {payload.get('id', 'unknown')}")
        return jwt.encode(
            token_payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            decoded = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
            logger.info(f"Successfully verified JWT token for user: {decoded.get('id', 'unknown')}")
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Attempt to use expired JWT token")
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            raise ValueError("Invalid token")
