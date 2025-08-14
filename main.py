from contextlib import asynccontextmanager
import os
from typing import Annotated
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import jwt
import requests
from sqlmodel import Session

import db
from models import User


load_dotenv()


engine = db.get_engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_db_and_tables(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]
WEB_REDIRECT_URI = os.environ["WEB_REDIRECT_URI"]
BACKEND_JWT_KEY = os.environ["BACKEND_JWT_KEY"]
SERVICE_ACCOUNT_ID = os.environ["SERVICE_ACCOUNT_ID"]
SERVICE_ACCOUNT_KEY = os.environ["SERVICE_ACCOUNT_KEY"]


@app.get("/")
async def get_root():
    return "Connie4 Server"


@app.get("/login/google")
async def login_google(web: bool = False):
    redirect_uri = WEB_REDIRECT_URI if web else GOOGLE_REDIRECT_URI
    url = "https://accounts.google.com/o/oauth2/auth?response_type=code"
    url += f"&client_id={GOOGLE_CLIENT_ID}"
    url += f"&redirect_uri={redirect_uri}"
    url += "&scope=openid%20profile%20email&access_type=offline"
    return {"url": url}


@app.get("/auth/google")
async def auth_google(
    code: str, response: Response, session: SessionDep, web: bool = False
):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": WEB_REDIRECT_URI if web else GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=data)
    access_token = token_response.json().get("access_token")
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    user = User(
        email=user_info.json()["email"],
        google_access_token=access_token,
    )
    user.create_or_update(session)

    backend_token = jwt.encode(
        {"email": user.email}, BACKEND_JWT_KEY, algorithm="HS256"
    )

    return {"token": backend_token}


@app.get("/token")
async def get_token(token: Annotated[str, Depends(oauth2_scheme)]):
    # todo Not sure how this fits into things
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    token_data = jwt.decode(token, BACKEND_JWT_KEY, algorithms=["HS256"])
    user = session.get(User, token_data["email"])
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="No current user found")


@app.get("/events")
async def read_events(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "data": [
            {"type": "event", "id": 12532, "attributes": {"name": "Event 1"}},
            {"type": "event", "id": 6782, "attributes": {"name": "Event 2"}},
        ]
    }
