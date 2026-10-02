from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import requests
import urllib.parse


import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.getenv(
    "LINKEDIN_REDIRECT_URI", "http://localhost:3000/linkedin/callback"
)
STATE = os.getenv("LINKEDIN_STATE", "kailash_csrf")

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


@app.get("/linkedin/connect")
def linkedin_connect():
    scope = "profile email openid w_member_social"

    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": scope,
        "state": STATE,
    }

    encoded_params = urllib.parse.urlencode(params)
    encoded_params = encoded_params.replace("+", "%20")
    url = f"{AUTH_URL}?{encoded_params}"

    return RedirectResponse(url=url)


@app.get("/linkedin/callback")
async def linkedin_callback(request: Request, code: str = None, state: str = None):
    """
    LinkedIn OAuth callback to exchange 'code' for an access token.
    """
    if not code or state != STATE:
        raise HTTPException(
            status_code=400, detail="Invalid authorization code or state mismatch"
        )

    payload = {
        # "grant_type": "authorization_code",
        "grant_type": "refresh_token",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }

    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token")

    print(response.json())

    access_token = response.json().get("access_token")
    if access_token:
        response = await user_profile(access_token)

    return {
        "access_token": access_token,
        "message": "Successfully connected to LinkedIn",
        "user_info": response,
    }


async def user_profile(access_token: str):
    """
    Fetch LinkedIn organizational page performance data using the access token.
    """
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Failed to fetch LinkedIn profile data"
        )
    return response.json()


# Root Endpoint
@app.get("/")
def root():
    return {"message": "LinkedIn OAuth FastAPI Integration"}
