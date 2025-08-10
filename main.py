import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
import requests


load_dotenv()


app = FastAPI()

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


class User(BaseModel):
    username: str
    email: str
    token: str


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


users = {}


def add_user():
    pass


@app.get("/auth/google")
async def auth_google(code: str, response: Response, web: bool = False):
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

    backend_token = jwt.encode(
        {"email": user_info.json()["email"]},
        BACKEND_JWT_KEY,
        algorithm="HS256"
    )

    return {
        "token": backend_token
    }


@app.get("/token")
async def get_token(token: Annotated[str, Depends(oauth2_scheme)]):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])


def user_from_token(token):
    return User(
        username="Fake User",
        email="fake@user.com",
        token=token,
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print(f"{token=}")
    user = user_from_token(token)
    return user


@app.get("/events")
async def read_events(current_user: Annotated[User, Depends(get_current_user)]):
    print(current_user)
    return {
        "data": [{
            "type": "event",
            "id": 12532,
            "attributes": {
                "name": "Event 1"
            }
        }, {
            "type": "event",
            "id": 6782,
            "attributes": {
                "name": "Event 2"
            }
        }]
    }
