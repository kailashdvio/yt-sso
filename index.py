# from fastapi import FastAPI
# from starlette.requests import Request
# from fastapi_sso.sso.google import GoogleSSO


# app = FastAPI()

# CLIENT_ID = os.getenv("GOOGLE_SSO_CLIENT_ID", "your_client_id")
# CLIENT_SECRET = os.getenv("GOOGLE_SSO_CLIENT_SECRET", "your_client_secret")

# google_sso = GoogleSSO(
#     CLIENT_ID, CLIENT_SECRET, os.getenv("GOOGLE_SSO_REDIRECT_URI", "http://localhost:3000/google/callback")
# )


# @app.get("/up")
# async def alive():
#     return "I am alive. Missing Ish"


# @app.get("/google/login")
# async def google_login():
#     with google_sso:
#         return await google_sso.get_login_redirect()


# @app.get("/google/callback")
# async def google_callback(request: Request):
#     with google_sso:
#         user = await google_sso.verify_and_process(request)
#     return user


from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
import requests
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:3000/connector/google-business"
)


@app.get("/google/login")
async def google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=https://www.googleapis.com/auth/business.manage"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url=google_auth_url)


# async def google_login():
#     google_auth_url = (
#         f"https://accounts.google.com/o/oauth2/auth?response_type=code"
#         f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
#         f"&scope=https://www.googleapis.com/auth/yt-analytics.readonly"
#         f"&access_type=offline"
#         f"&prompt=consent"
#     )
#     return google_auth_url


@app.get("/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")

    print("Code_", code)

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    token_response = await exchange_code_for_token(code)
    print(token_response)
    access_token = token_response.get("access_token")

    print("AccessToken_", access_token)
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found")

    # youtube_job_info = await create_youtube_reporting_job(access_token)
    # youtube_job_info = await get_business_profile(access_token)

    # return {"user_info": youtube_job_info}

    return access_token


async def exchange_code_for_token(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
        print("ExchangeChangeResponse_", response)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()


async def create_youtube_reporting_job(access_token: str):
    create_job_url = "https://youtubereporting.googleapis.com/v1/jobs"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {"reportTypeId": "channel_basic_a2", "name": "DVIO_ONE_JOB"}
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(create_job_url, headers=headers, json=payload)
    #     print(response.json())
    #     # response.raise_for_status()  # Raise an error for bad responses
    #     return response.json()

    response = requests.post(create_job_url, json=payload, headers=headers)

    print(response.json())

    return response.json()


async def get_business_profile(access_token: str):
    user_info_url = "https://mybusinessaccountmanagement.googleapis.com/v1/"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        print(response.json())
        # response.raise_for_status()  # Raise an error for bad responses
        return response.json()


async def get_user_info(access_token: str):
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()


# from fastapi import FastAPI, HTTPException
# from fastapi.responses import RedirectResponse
# from fastapi.requests import Request
# import httpx
# import requests

# app = FastAPI()

# CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
# CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://127.0.0.1:3000/google/callback")

# AIRBYTE_CLIENT_ID = os.getenv("AIRBYTE_CLIENT_ID", "")
# AIRBYTE_CLIENT_SECRET = os.getenv("AIRBYTE_CLIENT_SECRET", "")
# AIRBYTE_BASE_URL = os.getenv("AIRBYTE_BASE_URL", "https://api.airbyte.com/v1/")


# async def generate_airbyte_token(client_id, client_secret):
#     headers = {
#         "accept": "application/json",
#         "content-type": "application/json",
#     }
#     url = f"{AIRBYTE_BASE_URL}/applications/token"

#     response = requests.post(
#         url=url,
#         headers=headers,
#         json={
#             "client_id": client_id,
#             "client_secret": client_secret,
#         },
#     )

#     access_token = response.json()["access_token"]

#     return access_token


# @app.get("/google/login")
# async def google_login():
#     authHeader = f"Bearer {await generate_airbyte_token(AIRBYTE_CLIENT_ID, AIRBYTE_CLIENT_SECRET)}"

#     payload = {
#         "sourceType": "google-analytics-data-api",
#         "workspaceId": "b31bf4e8-de85-407e-b31a-6e6ad72a8f7b",
#         "redirectUrl": REDIRECT_URI,
#     }

#     headers = {
#         "accept": "application/json",
#         "content-type": "application/json",
#         "authorization": authHeader,
#     }

#     response = requests.post(
#         "https://api.airbyte.com/v1/sources/initiateOAuth",
#         json=payload,
#         headers=headers,
#     )

#     consentUrl = response.json()["consentUrl"]

#     google_auth_url = (
#         f"https://accounts.google.com/o/oauth2/auth?response_type=code"
#         f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
#         f"&scope=email%20profile%20https://www.googleapis.com/auth/adwords"
#         f"&access_type=offline"
#         # f"&scope=email%20profile%20https://www.googleapis.com/auth/adwords"
#     )
#     return RedirectResponse(url=consentUrl)


# @app.get("/google/callback")
# async def google_callback(request: Request):
#     code = request.query_params.get("code")
#     print("Code", code)
#     if not code:
#         raise HTTPException(status_code=400, detail="Authorization code not found")

#     token_response = await exchange_code_for_token(code)
#     print("Token response", token_response)
#     access_token = token_response.get("access_token")

#     if not access_token:
#         raise HTTPException(status_code=400, detail="Access token not found")

#     # user_info = await get_user_info(access_token)
#     google_ads_accounts = await get_google_ads_accounts(access_token)

#     # return {"user_info": user_info, "google_ads_accounts": google_ads_accounts}
#     return {"google_ads_accounts": google_ads_accounts}


# async def exchange_code_for_token(code: str):
#     token_url = "https://oauth2.googleapis.com/token"
#     payload = {
#         "code": code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(token_url, data=payload)
#         print("Exchange_Token", response.json())
#         response.raise_for_status()
#         return response.json()


# # async def get_user_info(access_token: str):
# #     user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
# #     headers = {"Authorization": f"Bearer {access_token}"}

# #     async with httpx.AsyncClient() as client:
# #         response = await client.get(user_info_url, headers=headers)
# #         response.raise_for_status()
# #         return response.json()


# async def get_google_ads_accounts(access_token: str):
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json",
#         "developer-token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
#     }
#     # Make a request to the Google Ads API to get the accounts
#     url = "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers"  # Adjust API version as needed

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             print(response.json())
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(e)


# @app.get("/request-access/{customer_id}")
# async def request_access(customer_id: str):
#     # Here you can handle the logic to request access to the Google Ads account.
#     # This might involve presenting a consent screen or storing the customer ID for future use.
#     return {
#         "message": f"Requesting access to Google Ads account with customer ID: {customer_id}"
#     }


"""
{"type":"SPEC","spec":{"connectionSpecification":{"$schema":"http://json-schema.org/draft-07/schema#","title":"YouTube Analytics Spec","type":"object","required":["credentials"],"additionalProperties":true,"properties":{"credentials":{"title":"Authenticate via OAuth 2.0","type":"object","required":["client_id","client_secret","refresh_token"],"additionalProperties":true,"properties":{"client_id":{"title":"Client ID","type":"string","description":"The Client ID of your developer application","airbyte_secret":true},"client_secret":{"title":"Client Secret","type":"string","description":"The client secret of your developer application","airbyte_secret":true},"refresh_token":{"title":"Refresh Token","type":"string","description":"A refresh token generated using the above client ID and secret","airbyte_secret":true}}}}},"documentationUrl":"https://docs.airbyte.com/integrations/sources/youtube-analytics","supportsNormalization":false,"supportsDBT":false,"advanced_auth":{"auth_flow_type":"oauth2.0","oauth_config_specification":{"complete_oauth_output_specification":{"type":"object","additionalProperties":true,"properties":{"refresh_token":{"type":"string","path_in_connector_config":["credentials","refresh_token"]}}},"complete_oauth_server_input_specification":{"type":"object","additionalProperties":true,"properties":{"client_id":{"type":"string"},"client_secret":{"type":"string"}}},"complete_oauth_server_output_specification":{"type":"object","additionalProperties":true,"properties":{"client_id":{"type":"string","path_in_connector_config":["credentials","client_id"]},"client_secret":{"type":"string","path_in_connector_config":["credentials","client_secret"]}}}}}}}
{"type":"CONNECTION_STATUS","connectionStatus":{"status":"FAILED","message":"Config validation error: 'credentials' is a required property"}}
{"type":"LOG","log":{"level":"FATAL","message":"'credentials' is a required property\nTraceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/airbyte-integrations/connectors/source-youtube-analytics/source_youtube_analytics/run.py\", line 14, in run\n    launch(source, sys.argv[1:])\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 341, in launch\n    for message in source_entrypoint.run(parsed_args):\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 163, in run\n    yield from map(\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 229, in discover\n    self.validate_connection(source_spec, config)\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 285, in validate_connection\n    check_config_against_spec_or_exit(connector_config, source_spec)\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/sources/utils/schema_helpers.py\", line 182, in check_config_against_spec_or_exit\n    raise AirbyteTracedException(\nairbyte_cdk.utils.traced_exception.AirbyteTracedException: 'credentials' is a required property"}}
{"type":"TRACE","trace":{"type":"ERROR","emitted_at":1749800519385,"error":{"message":"Config validation error: 'credentials' is a required property","internal_message":"'credentials' is a required property","stack_trace":"Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/airbyte-integrations/connectors/source-youtube-analytics/source_youtube_analytics/run.py\", line 14, in run\n    launch(source, sys.argv[1:])\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 341, in launch\n    for message in source_entrypoint.run(parsed_args):\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 163, in run\n    yield from map(\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 229, in discover\n    self.validate_connection(source_spec, config)\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 285, in validate_connection\n    check_config_against_spec_or_exit(connector_config, source_spec)\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/sources/utils/schema_helpers.py\", line 182, in check_config_against_spec_or_exit\n    raise AirbyteTracedException(\nairbyte_cdk.utils.traced_exception.AirbyteTracedException: 'credentials' is a required property\n","failure_type":"config_error"}}}
{"type":"LOG","log":{"level":"FATAL","message":"[Errno 2] No such file or directory: 'sample_files/configured_catalog.json'\nTraceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/airbyte-integrations/connectors/source-youtube-analytics/source_youtube_analytics/run.py\", line 14, in run\n    launch(source, sys.argv[1:])\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 341, in launch\n    for message in source_entrypoint.run(parsed_args):\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 168, in run\n    config_catalog = self.source.read_catalog(parsed_args.catalog)\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/sources/source.py\", line 90, in read_catalog\n    return ConfiguredAirbyteCatalogSerializer.load(cls._read_json_file(catalog_path))\n                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/connector.py\", line 55, in _read_json_file\n    with open(file_path, \"r\") as file:\n         ^^^^^^^^^^^^^^^^^^^^\nFileNotFoundError: [Errno 2] No such file or directory: 'sample_files/configured_catalog.json'"}}
{"type":"TRACE","trace":{"type":"ERROR","emitted_at":1749800520682,"error":{"message":"Something went wrong in the connector. See the logs for more details.","internal_message":"[Errno 2] No such file or directory: 'sample_files/configured_catalog.json'","stack_trace":"Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/airbyte-integrations/connectors/source-youtube-analytics/source_youtube_analytics/run.py\", line 14, in run\n    launch(source, sys.argv[1:])\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 341, in launch\n    for message in source_entrypoint.run(parsed_args):\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/entrypoint.py\", line 168, in run\n    config_catalog = self.source.read_catalog(parsed_args.catalog)\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/sources/source.py\", line 90, in read_catalog\n    return ConfiguredAirbyteCatalogSerializer.load(cls._read_json_file(catalog_path))\n                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/kailash-bisht/Desktop/test_connector/airbyte/.venv/lib/python3.12/site-packages/airbyte_cdk/connector.py\", line 55, in _read_json_file\n    with open(file_path, \"r\") as file:\n         ^^^^^^^^^^^^^^^^^^^^\nFileNotFoundError: [Errno 2] No such file or directory: 'sample_files/configured_catalog.json'\n","failure_type":"system_error"}}}
"""
