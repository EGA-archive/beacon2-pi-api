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
def fetch_idp(self, access_token, test_mode=False):
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
        idp_issuer=None
        # Iterate through the different accepted idp providers and check if there is one that matches the issuer of the token
        for client_type in ['confidential', 'public']:
            for env_filename in glob.glob("beacon/auth/idp_providers/{}/*.env".format(client_type)):
                load_dotenv(env_filename, override=True)
                idp_issuer = os.getenv('ISSUER')
                # In case the issuer matches, set the idp values to be used later for validating the token
                if issuer == idp_issuer:
                    idp_well_known_endpoint = os.getenv('WELL_KNOWN_ENDPOINT')
                    response = requests.get(idp_well_known_endpoint)
                    response.raise_for_status()
                    well_known_info = response.json()
                    user_info= well_known_info["userinfo_endpoint"]
                    idp_jwks_url=well_known_info["jwks_uri"]
                    idp_introspection=well_known_info["introspection_endpoint"]
                    if test_mode==True:
                        if 'localhost' in user_info:
                            user_info=user_info.replace('localhost','idp')
                        if 'localhost' in idp_jwks_url:
                            idp_jwks_url=idp_jwks_url.replace('localhost','idp')
                        if 'localhost' in idp_introspection:
                            idp_introspection=idp_introspection.replace('localhost', 'idp')
                    idp_client_id = os.getenv('CLIENT_ID')
                    if client_type == 'confidential':
                        idp_client_secret = os.getenv('CLIENT_SECRET')
                    else:
                        idp_client_secret=None
                    aud_must_include_url = os.getenv('MUST_INCLUDE_BEACON_URL_IN_AUDIENCE')
                    if aud_must_include_url == True:
                        if config.complete_url not in aud:
                            self.LOG.warning("Unauthorized. The beacon's url is not included in the audience of the access token.")
                            raise NoPermissionsAvailable("Unauthorized. The beacon's url is not included in the audience of the access token.")
                    break
                else:
                    continue
    except Exception as e:
        self.LOG.warning(e)
    if idp_issuer is None:
        self.LOG.warning("Unauthorized. There is no issuer in the token. Please, use a valid token with an issuer header.")
        raise NoPermissionsAvailable("Unauthorized. There is no issuer in the token. Please, use a valid token with an issuer header.")
    return idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, aud

'''
@log_with_args(config.level)
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

@log_with_args(config.level)
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
                except Exception:
                    self.LOG.warning("No GA4GH visas found for the user")
                    visa_datasets=None
                finally:
                    if visa_datasets is not None:
                        for visa_dataset in visa_datasets:
                            # Validate the visas and extract the datasets ids
                            try:
                                visa = jwt.decode(visa_dataset, options={"verify_signature": False}, algorithms=["RS256"])
                                if visa['iss'] in config.ga4gh_visa_trusted_issuers:
                                    pass
                                else:
                                    self.LOG.warning("Unauthorized visa: {}. Issuer not trusted.".format(visa_dataset))
                                    raise NoPermissionsAvailable("Unauthorized visa. Issuer not trusted.")
                                visa_jwks_url=visa['iss']+'.well-known/openid-configuration'
                                visa_validated = validate_ga4gh_visa(self, access_token, visa['iss'], visa_jwks_url)
                                if visa_validated==True:
                                    with open("/beacon/permissions/ga4gh_visas/visas_conf.yml", 'r') as pfile:
                                        visas_conf = yaml.safe_load(pfile)
                                    pfile.close()
                                    visa_values=visa['ga4gh_visa_v1']
                                    accepted_visa=False
                                    if visa_values['type']=='AcceptedTermsAndPolicies':
                                        for trusted_acceptedterms_visa in visas_conf['AcceptedTermsAndPolicies']:
                                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                                    accepted_visa=True
                                                    break
                                        if accepted_visa==False:
                                            self.LOG.warning('Terms and Conditions not accepted for the user')
                                            raise NoTermsAndConditionsForResearcherAvailable('Terms and Conditions not accepted for the user')
                                    elif visa_values['type']=='ResearcherStatus':
                                        for trusted_acceptedterms_visa in visas_conf['ResearcherStatus']:
                                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                                    accepted_visa=True
                                                    break
                                        if accepted_visa==False:
                                            self.LOG.warning('Researcher Status: {} is not accepted'.format(visa_values['value']))
                                            raise NoTermsAndConditionsForResearcherAvailable('Researcher Status is not RESEARCHER')
                                    elif visa_values['type']=='ControlledAccessGrants':
                                        for trusted_acceptedterms_visa in visas_conf['ControlledAccessGrants']:
                                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                                    accepted_visa=True
                                                    dataset_url = visa["ga4gh_visa_v1"]["value"]
                                                    dataset_url_splitted = dataset_url.split('/')
                                                    visa_dataset = dataset_url_splitted[-1]
                                                    list_visa_datasets.append(visa_dataset)
                                                    break
                                        if accepted_visa==False:
                                            self.LOG.warning('Invalid datasets visa')
                                            raise NoTermsAndConditionsForResearcherAvailable('Invalid Visa')
                            except Exception as e:
                                self.LOG.warning("Invalid GA4GH Visa: {}".format(visa_dataset))
                                visa_dataset = None
                return user, list_visa_datasets
            else:
                raise NoPermissionsAvailable("Unauthorized. Could not fetch the user info from the token.")

@log_with_args(config.level)
async def authentication(self, access_token, test_mode=False):
    # Initiate the lisst of the datasets permissions that come from visas
    list_visa_datasets=[]
    try:
        idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, aud = fetch_idp(self, access_token, test_mode)
        access_token_validation = validate_access_token(self, access_token, idp_issuer, idp_jwks_url, aud)
        if access_token_validation == True:
            user, list_visa_datasets = await fetch_user_info(self, access_token, user_info, idp_issuer, list_visa_datasets)
            return user, list_visa_datasets
    except NoTermsAndConditionsForResearcherAvailable:
        raise
    except Exception as e:
        #LOG.debug(e)
        #access_token_validation = await introspection(idp_introspection, idp_client_id, idp_client_secret, access_token, list_visa_datasets)
        user = None
        list_visa_datasets=[]
        return user, list_visa_datasets