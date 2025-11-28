import logging
import jwt
import glob
from aiohttp import ClientSession, BasicAuth, FormData
from aiohttp import web
import os
from dotenv import load_dotenv
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.exceptions.exceptions import NoPermissionsAvailable
import re

@log_with_args(level)
def validate_access_token(self, access_token, idp_issuer, jwks_url, algorithm, aud):
    if not jwt.algorithms.has_crypto:
        raise NoPermissionsAvailable("Unauthorized. The token is not encrypted with an algorithm.")
    try:
        # Decode the token with the jwks keys
        jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=[algorithm],
            issuer=idp_issuer,
            audience=aud,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
        return True
    except jwt.exceptions.PyJWTError as err:
        pass

@log_with_args(level)
def fetch_idp(self, access_token):
    try:
        # Get the payload values of the token
        header = jwt.get_unverified_header(access_token)
        algorithm=header["alg"]
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        issuer = decoded['iss']
        aud = decoded['aud']
    except Exception as e:
        raise NoPermissionsAvailable("Unauthorized. The token could not be decoded")
    # Initialize the user and idp issuer info variables
    user_info=''
    idp_issuer=None
    # Iterate through the different accepted idp providers and check if there is one that matches the issuer of the token
    for env_filename in glob.glob("beacon/auth/idp_providers/*.env"):
        load_dotenv(env_filename, override=True)
        IDP_ISSUER = os.getenv('ISSUER')
        IDP_ISSUER = re.findall(r'[a-zA-Z0-9:/-]', IDP_ISSUER)
        IDP_ISSUER = "".join(r for r in IDP_ISSUER)
        IDP_ISSUER = str(IDP_ISSUER)
        # In case the issuer matches, set the idp values to be used later for validating the token
        if issuer == IDP_ISSUER:
            IDP_CLIENT_ID = os.getenv('CLIENT_ID')
            IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
            IDP_USER_INFO = os.getenv('USER_INFO')
            IDP_USER_INFO = re.findall(r'[a-zA-Z0-9:/-]', IDP_USER_INFO)
            IDP_USER_INFO = "".join(r for r in IDP_USER_INFO)
            IDP_USER_INFO = str(IDP_USER_INFO)
            IDP_INTROSPECTION = os.getenv('INTROSPECTION')
            IDP_JWKS_URL = os.getenv('JWKS_URL')
            idp_issuer = IDP_ISSUER
            user_info = IDP_USER_INFO
            idp_client_id = IDP_CLIENT_ID
            idp_client_secret = IDP_CLIENT_SECRET
            idp_introspection = IDP_INTROSPECTION
            idp_jwks_url = IDP_JWKS_URL
            break
        else:
            continue
    if idp_issuer is None:
        raise NoPermissionsAvailable("Unauthorized. There is no issuer in the token. Please, use a valid token with an issuer header.")
    return idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, algorithm, aud

'''
@log_with_args(level)
async def introspection(self, idp_introspection, idp_client_id, idp_client_secret, access_token, list_visa_datasets):
    async with ClientSession() as session:
        async with session.post(idp_introspection,
                                auth=BasicAuth(idp_client_id, password=idp_client_secret),
                                data=FormData({ 'token': access_token, 'token_type_hint': 'access_token' }, charset='UTF-8')
        ) as resp:
            #content = await resp.text()
            if resp.status == 200:
                return True
            else:
                return False
'''

@log_with_args(level)
async def fetch_user_info(self, access_token, user_info, idp_issuer, list_visa_datasets):
    # Get the user info endoint of the idp with the token and the idp parameters provided
    async with ClientSession(trust_env=True) as session:
        headers = { 'Accept': 'application/json', 'Authorization': 'Bearer ' + access_token }
        async with session.get(user_info, headers=headers) as resp:
            if resp.status == 200:
                # If the response is good, get the user info of the esponse
                user = await resp.json()
                try:
                    # Check if there are ny visas in the user info of the response
                    visa_datasets = user['ga4gh_passport_v1']
                    if visa_datasets is not None:
                        for visa_dataset in visa_datasets:
                            # Validate the visas and extract the datasets ids
                            try:
                                visa = jwt.decode(visa_dataset, options={"verify_signature": False}, algorithms=["RS256"])
                                if visa['iss']==idp_issuer:
                                    pass
                                else:
                                    raise NoPermissionsAvailable("Unauthorized. Invalid visa token.")
                                dataset_url = visa["ga4gh_visa_v1"]["value"]
                                dataset_url_splitted = dataset_url.split('/')
                                visa_dataset = dataset_url_splitted[-1]
                                list_visa_datasets.append(visa_dataset)
                            except Exception:
                                visa_dataset = None
                except Exception:
                    pass
                return user, list_visa_datasets
            else:
                raise NoPermissionsAvailable("Unauthorized. Could not fetch the user info from the token.")

@log_with_args(level)
async def authentication(self, access_token):
    # Initiate the lisst of the datasets permissions that come from visas
    list_visa_datasets=[]
    try:
        idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, algorithm, aud = fetch_idp(self, access_token)
        access_token_validation = validate_access_token(self, access_token, idp_issuer, idp_jwks_url, algorithm, aud)
        if access_token_validation == True:
            user, list_visa_datasets = await fetch_user_info(self, access_token, user_info, idp_issuer, list_visa_datasets)
            return user, list_visa_datasets
    except Exception as e:
        #LOG.debug(e)
        #access_token_validation = await introspection(idp_introspection, idp_client_id, idp_client_secret, access_token, list_visa_datasets)
        user = 'public'
        list_visa_datasets=[]
        return user, list_visa_datasets