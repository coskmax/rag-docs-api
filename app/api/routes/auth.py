from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.database import get_session
from app.db.users import create_user, get_user, verify_password
from app.schemas.auth import RegisterRequest, RegisterResponse, TokenRequest, TokenResponse

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_session)) -> RegisterResponse:
    if get_user(db, request.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    create_user(db, request.username, request.password)
    return RegisterResponse(username=request.username, message="User created successfully")


@router.post("/token", response_model=TokenResponse)
def login(request: TokenRequest, db: Session = Depends(get_session)) -> TokenResponse:
    if not verify_password(db, request.username, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=token)
