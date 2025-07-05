from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

SECRET_KEY = '96cb5e02cadf7a47bf66e393c0ea4b7de24afa726fcc0447a7c54b7a6e8ce650'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    """Генерирует хеш пароля."""
    return pwd_context.hash(password)
