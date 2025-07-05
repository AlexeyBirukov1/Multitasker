import secrets
from sqlalchemy.orm import Session
from db.models import User
from services.auth_services import get_password_hash
def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def request_password_reset(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    db.commit()
    return reset_token

def reset_password(db: Session, token: str, new_password: str) -> bool:
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        return False

    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    return True