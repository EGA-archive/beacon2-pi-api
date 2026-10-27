import jwt
import glob
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import NoPermissionsAvailable, NoTermsAndConditionsForResearcherAvailable
import requests
import yaml

@log_with_args(config.level)
def validate_access_token(self, access_token, idp_issuer, jwks_url, aud):
    if not jwt.algorithms.has_crypto:
        raise NoPermissionsAvailable("Unauthorized. The token is not encrypted with an algorithm.")
    try:
        # Decode the token with the jwks keys
        jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=config.access_token_accepted_algorithms,
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
        return False

@log_with_args(config.level)
def check_needed_visa_conf(self, visas_conf, visas_outcome):
    for visa_type, conditions in visas_conf.items():
        if conditions['enabled']==True:
            if visa_type in visas_outcome:
                if visas_outcome[visa_type]==False:
                    self.LOG.warning('{} condition was not met'.format(visa_type))
                    raise NoTermsAndConditionsForResearcherAvailable('{} condition was not met'.format(visa_type))
            else:
                self.LOG.warning('{} condition was not met'.format(visa_type))
                raise NoTermsAndConditionsForResearcherAvailable('{} condition was not met'.format(visa_type))

@log_with_args(config.level)
def validate_ga4gh_visa(self, visa_token, visa_issuer, jwks_url):
    if not jwt.algorithms.has_crypto:
        raise NoPermissionsAvailable("Unauthorized. The token is not encrypted with an algorithm.")
    try:
        # Decode the token with the jwks keys
        jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
        signing_key = jwks_client.get_signing_key_from_jwt(visa_token)
        data = jwt.decode(
            visa_token,
            signing_key.key,
            algorithms=config.ga4gh_visa_accepted_algorithms,
            issuer=visa_issuer,
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
        return False

@log_with_args(config.level)
def get_grants_from_visas(self, visa_tokens, list_visa_tokens):
    with open("/beacon/permissions/ga4gh_visas/visas_conf.yml", 'r') as pfile:
        visas_conf = yaml.safe_load(pfile)
    pfile.close()
    if visa_tokens is not None:
        visas_outcome={}
        for visa_token in visa_tokens:
            # Validate the visas and extract the datasets ids
            try:
                accepted_issuer=False
                for visa_type,conditions in visas_conf.items():
                    
                    if conditions['enabled']==True:
                        if visa_type not in visas_outcome:
                            if visa_type == 'ControlledAccessGrants':
                                visas_outcome[visa_type]=None
                            else:
                                visas_outcome[visa_type]=False
                        elif visas_outcome[visa_type]==True:
                            continue
                    else:
                        continue
                    visa = jwt.decode(visa_token, options={"verify_signature": False}, algorithms=["RS256"])
                    if 'ga4gh_visa_v1' in visa:
                        visa_values=visa['ga4gh_visa_v1']
                        if visa_values['type']==visa_type:
                            for issuer in conditions['issuers']:
                                if visa['iss'] == issuer['iss']:
                                    accepted_issuer=True
                                    visa_jwks_url=issuer["jwks_uri"]
                                    break
                            if accepted_issuer==False:
                                self.LOG.warning("Unauthorized visa. Issuer not trusted.")
                                raise NoPermissionsAvailable("Unauthorized visa. Issuer not trusted.")
                            accepted_issuer=False
                            visa_validated = validate_ga4gh_visa(self, visa_token, visa['iss'], visa_jwks_url)
                            if visa_validated == False:
                                self.LOG.warning("Unauthorized visa. Visa not valid.")
                                raise NoPermissionsAvailable("Unauthorized visa. Visa not valid.")
                            for issuers_values in conditions['issuers']:
                                if visa_values['value'] in issuers_values["accepted_values"]:
                                    if visa["iss"] == issuers_values["iss"]:
                                        if visa_type == 'ControlledAccessGrants':
                                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                                            dataset_url_splitted = dataset_url.split('/')
                                            visa_dataset = dataset_url_splitted[-1]
                                            list_visa_tokens.append(visa_dataset)
                                            visas_outcome[visa_type]=visa_dataset
                                        else:
                                            visas_outcome[visa_type]=True
                                        break
                        else:
                            continue
            except Exception as e:
                continue
        return list_visa_tokens, visas_outcome, visas_conf
    return list_visa_tokens, {}, visas_conf

@log_with_args(config.level)
def fetch_idp(self, access_token):
    idp_issuer=None
    try:
        # Get the payload values of the token
        header = jwt.get_unverified_header(access_token)
        algorithm=header["alg"]
        decoded = jwt.decode(access_token, options={"verify_signature": False})
    except Exception as e:
        self.LOG.warning("Unauthorized. The token could not be decoded")
        raise NoPermissionsAvailable("Unauthorized. The token could not be decoded")
    if algorithm not in config.access_token_accepted_algorithms:
        self.LOG.warning('Invalid token. Algorithm for the access token is not accepted')
        raise NoPermissionsAvailable('Invalid token. Algorithm for the access token is not accepted')
    issuer = decoded['iss']
    try:
        aud = decoded['aud']

        # Initialize the user and idp issuer info variables
        user_info=''
        # Iterate through the different accepted idp providers and check if there is one that matches the issuer of the token
        for env_filename in glob.glob("beacon/auth/idp_providers/*.env"):
            load_dotenv(env_filename, override=True)
            idp_issuer = os.getenv('ISSUER')
            # In case the issuer matches, set the idp values to be used later for validating the token
            if issuer == idp_issuer:
                idp_well_known_endpoint = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(idp_well_known_endpoint, timeout=2)
                response.raise_for_status()
                well_known_info = response.json()
                user_info= well_known_info["userinfo_endpoint"]
                idp_jwks_url=well_known_info["jwks_uri"]
                idp_introspection=well_known_info["introspection_endpoint"]
                if 'testing_idp' in env_filename:
                    if 'localhost' in user_info:
                        user_info=user_info.replace('localhost','idp')
                    if 'localhost' in idp_jwks_url:
                        idp_jwks_url=idp_jwks_url.replace('localhost','idp')
                    if 'localhost' in idp_introspection:
                        idp_introspection=idp_introspection.replace('localhost', 'idp')
                idp_client_id = os.getenv('CLIENT_ID')
                if isinstance(aud, str):
                    aud = [aud]
                if idp_client_id not in aud:
                    raise NoPermissionsAvailable("Unauthorized. The client is not included in the audience of the access token.")
                aud_must_include_url = os.getenv('MUST_INCLUDE_BEACON_URL_IN_AUDIENCE')
                if isinstance(aud_must_include_url, str):
                    if aud_must_include_url == 'True' or aud_must_include_url == 'true':
                        aud_must_include_url=True
                    else:
                        aud_must_include_url=False
                if aud_must_include_url == True:
                    if config.complete_url not in aud:
                        raise NoPermissionsAvailable("Unauthorized. The beacon's url is not included in the audience of the access token.")
                if len(aud)==1:
                    aud=aud[0]
                break
            else:
                continue
    except Exception as e:
        idp_issuer=None
        self.LOG.warning(e)
    if idp_issuer is None:
        self.LOG.warning("Unauthorized. There is no valid issuer in the token. Please, use a valid token that matches one of the configured identity providers.")
        raise NoPermissionsAvailable("Unauthorized. There is no issuer in the token. Please, use a valid token with an issuer header.")
    return idp_issuer, user_info, idp_jwks_url, aud

@log_with_args(config.level)
async def fetch_user_info(self, access_token, user_info, idp_issuer, list_visa_tokens):
    # Get the user info endoint of the idp with the token and the idp parameters provided
    async with ClientSession(trust_env=True) as session:
        headers = { 'Accept': 'application/json', 'Authorization': 'Bearer ' + access_token }
        async with session.get(user_info, headers=headers) as resp:
            if resp.status == 200:
                # If the response is good, get the user info of the esponse
                user = await resp.json()
                try:
                    # Check if there are any visas in the user info of the response
                    visa_tokens = user['ga4gh_passport_v1']
                except Exception:
                    self.LOG.warning("No GA4GH visas found for the user")
                    visa_tokens=None
                finally:
                    list_visa_tokens, visas_outcome, visas_conf = get_grants_from_visas(self, visa_tokens, list_visa_tokens)
                check_needed_visa_conf(self, visas_conf, visas_outcome)
                return user, list_visa_tokens
            else:
                self.LOG.warning('Unauthorized. Could not fetch the user info from the token.')
                raise NoPermissionsAvailable("Unauthorized. Could not fetch the user info from the token.")

@log_with_args(config.level)
async def authentication(self, access_token):
    # Initiate the lisst of the datasets permissions that come from visas
    list_visa_tokens=[]
    try:
        idp_issuer, user_info, idp_jwks_url, aud = fetch_idp(self, access_token)
        access_token_validation = validate_access_token(self, access_token, idp_issuer, idp_jwks_url, aud)
        if access_token_validation == True:
            user, list_visa_tokens = await fetch_user_info(self, access_token, user_info, idp_issuer, list_visa_tokens)
            return user, list_visa_tokens
    except NoTermsAndConditionsForResearcherAvailable:
        raise
    except Exception as e:
        user = None
        list_visa_tokens=[]
        return user, list_visa_tokens