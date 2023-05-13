from datetime import datetime, timedelta

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import UserInfo
from schemas import UserRead, UserUpdate, UserCreate, Token

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token"))):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    token_data = Token(username=username)
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    db_user = UserInfo(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_session)):
    db_user = await db.get(UserInfo, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserRead])
async def read_users(
        page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_session)
):
    users = await db.execute(select(UserInfo).offset((page - 1) * per_page).limit(per_page))
    total_users = await db.execute(select(func.count(UserInfo.id)))
    total_users = total_users.scalar_one()
    total_pages = (total_users + per_page - 1) // per_page
    return {"users": users.scalars().all(), "total_pages": total_pages, "total_users": total_users}

