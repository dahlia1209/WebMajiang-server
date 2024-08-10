# routers/garootme.py
from fastapi_azure_auth import B2CMultiTenantAuthorizationCodeBearer, user
from fastapi import APIRouter,Depends
from dependencies import get_settings

router = APIRouter()

azure_scheme = B2CMultiTenantAuthorizationCodeBearer(
    app_client_id=get_settings().APP_CLIENT_ID,
    openid_config_url=get_settings().OPENID_CONFIG_URL,
    openapi_authorization_url=get_settings().OPENAPI_AUTHORIZATION_URL,
    openapi_token_url=get_settings().OPENAPI_TOKEN_URL,
    scopes=get_settings().SCOPES,
    validate_iss=False,
)


@router.get("/")
async def root(token: user.User = Depends(azure_scheme)):
    return {"message": "Hello World"}