
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level, uri, uri_subpath, api_version
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import IncoherenceInRequestError, InvalidRequest, WrongURIPath, NoFiltersAllowed
import html
from beacon.models.ga4gh.beacon_v2_default_model.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.conf import filtering_terms
import os
from beacon.request.parameters import RequestMeta, SchemasPerEntity
from pydantic import ValidationError
from beacon.utils.modules import get_conf

@log_with_args(level)
def parse_query_string(self, request):
    '''
    Here we process the query string dictionary, which comes in a multidict (request.query) with each of the parameters as key of the dict and we transform it in a dictionary
    that validates against a beacon v2 json body request.
    '''
    query_string_body={}
    query_string_body["query"]={}
    query_string_body["query"]["requestParameters"]={}
    query_string_body["meta"]={}
    for k, v in request.query.items():
        v = html.escape(v)
        if k == 'filters':
            v_list=[]
            if ',' in v:
                v_list =v.split(',')
            else:
                v_list.append(v)
            query_string_body["query"]["filters"]=[]
            for id in v_list:
                v_dict={}
                v_dict['id']=id
                query_string_body["query"]["filters"].append(v_dict)
        elif k == 'includeResultsetResponses':
            query_string_body["query"]["includeResultsetResponses"] = v
        elif k == 'skip':
            try:
                query_string_body["query"]["pagination"]["skip"] = v
            except Exception:
                query_string_body["query"]["pagination"]= {}
                query_string_body["query"]["pagination"]["skip"] = v
        elif k == 'limit':
            try:
                query_string_body["query"]["pagination"]["limit"] = v
            except Exception:
                query_string_body["query"]["pagination"]= {}
                query_string_body["query"]["pagination"]["limit"] = v
        elif k == 'testMode':
            query_string_body["query"]["testMode"] = v
        elif k == 'requestedSchemas':
            query_string_body["meta"]["requestedSchemas"] = [{"schema": v}]
        elif k == 'requestedGranularity':
            query_string_body["query"]["requestedGranularity"] = v
        elif k == 'datasets':
            query_string_body["query"]["requestParameters"][k]=[v]
        elif k in ["start", "end"]:
            if ',' in v:
                v_splitted = v.split(',')
                query_string_body["query"]["requestParameters"][k]=[int(v) for v in v_splitted]
            else:
                query_string_body["query"]["requestParameters"][k]=[int(v)]
        else:
            query_string_body["query"]["requestParameters"][k]=v
    if query_string_body["query"]["requestParameters"]=={}:
        query_string_body["query"].pop("requestParameters")
    if query_string_body["meta"]=={}:
        query_string_body.pop("meta")
    if query_string_body["query"]=={}:
        query_string_body.pop("query")
    return query_string_body

@log_with_args(level)
async def get_qparams(self, request): # anomenar query string en comptes de qparams
    # Bad Request not priority
    '''
    The function will catch all the parameters in the query string and see if they also exist in a json body of the request. If a parameter is found in both places and is different, we
    will return a Bad Request. After that, the params request will be validated against a pydantic class RequestParams and an instance of the object class will be 
    returned to have a variable called qparams with the query parameters that will be used for processing the query.
    '''
    try:
        query_string_body=parse_query_string(self, request)
        post_data = await request.json() if request.has_body else {}
        final_body=post_data
        for k, v in query_string_body.items():
            if post_data.get(k) == None:
                final_body[k]=v
            else:
                for k1, v1 in v.items():
                    if isinstance(v1, dict):
                        for k2, v2 in v1.items():
                            if post_data[k][k1].get(k2)==None:
                                final_body[k][k1][k2]=v2
                            elif post_data[k][k1][k2]!=v2:
                                raise IncoherenceInRequestError('two parameters conflict from string: {} and from json body query: {}'.format(v1, post_data[k][k1][k2]))
                    elif isinstance(v1, list):
                        for item in v1:
                            if item not in post_data[k][k1]:
                                final_body[k][k1].append(item)
                    elif post_data[k][k1]!=v1:
                        raise IncoherenceInRequestError('two parameters conflict from string: {} and from json body query: {}'.format(v1, post_data[k][k1]))
        qparams = RequestParams(**final_body).from_request(final_body)
        RequestAttributes.qparams = qparams
    except ValidationError:
        raise InvalidRequest('set of meta/query parameters: {} not allowed'.format(post_data))
    
@log_with_args(level)
def set_entry_type_configuration(self):
    '''
    On the action of checking if there is a match between the endpoint queried an entry type in configuration, we then grab the database (source), max_granularity (allowed_granularity)
    and id name of the records of the entry type to keep them in the RequestAttributes object for later.
    '''
    if RequestAttributes.entry_type == 'filtering_terms':
        RequestAttributes.source = filtering_terms.database
        RequestAttributes.allowed_granularity = 'record'
    elif RequestAttributes.entry_type == 'map':
        RequestAttributes.allowed_granularity = 'record'
    elif RequestAttributes.entry_type == 'configuration':
        RequestAttributes.allowed_granularity = 'record'
    elif RequestAttributes.entry_type == 'info':
        RequestAttributes.allowed_granularity = 'record'
    elif RequestAttributes.entry_type == 'service-info':
        RequestAttributes.allowed_granularity = 'record'
    elif RequestAttributes.entry_type == 'entry_types':
        RequestAttributes.allowed_granularity = 'record'
    else:
        endpoint_module = get_conf(RequestAttributes.entry_type)
        RequestAttributes.source = endpoint_module.database
        RequestAttributes.allowed_granularity = endpoint_module.granularity
        RequestAttributes.entry_type_id = endpoint_module.id
    
@log_with_args(level)
def set_entry_type(self, request):
    '''
    We receive an absolute url with a host and a port, the endpoint queried and the query string. We check that the url and host match with the beacon uri in conf and then
    we keep the name of the endpoint checking if it matches an entry type in configuration and the internal id queried, if there is one.
    '''
    abs_url_with_query_string=str(request.url)
    abs_url=abs_url_with_query_string.split('?')
    abs_url=abs_url[0]
    starting_endpoint = len(uri) + len(uri_subpath)
    def_uri = uri + uri_subpath
    if 'https' not in abs_url and 'https' in def_uri:
        abs_url = abs_url.replace('http', 'https')
    if abs_url[:starting_endpoint] != def_uri :
        LOG.warning('configuration variable uri: {} not the same as where the beacon is hosted'.format(uri))
    if abs_url_with_query_string.endswith('/api'):
        RequestAttributes.entry_type='info'
        set_entry_type_configuration(self)
    else:
        path_list = abs_url[starting_endpoint:].split('/')
        path_list = list(filter(None, path_list))
        if path_list == []:
            raise WrongURIPath('the {} parameter from conf.py is not the same as the root one received in request: {}. Configure you uri accordingly.'.format(uri, abs_url))
        if len(path_list) > 2:
            try:
                RequestAttributes.pre_entry_type=path_list[0]
                RequestAttributes.entry_type=path_list[2]
            except Exception:
                raise WrongURIPath('path received is wrong, check your uri: {} from conf file to make sure is correct'.format(uri))
            set_entry_type_configuration(self)
            RequestAttributes.entry_id=request.match_info.get('id', None)
        else:
            try:
                RequestAttributes.entry_type=path_list[0]
            except Exception:
                raise WrongURIPath('path received is wrong, check your uri: {} from conf file to make sure is correct'.format(uri))
            set_entry_type_configuration(self)
            RequestAttributes.entry_id=request.match_info.get('id', None)
    if RequestAttributes.entry_type not in ['filtering_terms', 'map', 'configuration', 'info', 'service-info', 'entry_types']:
        endpoint_module = get_conf(RequestAttributes.entry_type)
        RequestAttributes.mongo_collection = endpoint_module.database_connection

@log_with_args(level)
def set_response_type(self):
    '''
    We receive an absolute url with a host and a port, the endpoint queried and the query string. We check that the url and host match with the beacon uri in conf and then
    we keep the name of the endpoint checking if it matches an entry type in configuration and the internal id queried, if there is one.
    '''
    endpoint_module = get_conf(RequestAttributes.entry_type)
    LOG.warning(endpoint_module)
    if RequestAttributes.qparams.query.includeResultsetResponses != 'NONE':
        RequestAttributes.response_type = 'resultSet'
    elif RequestAttributes.qparams.query.includeResultsetResponses == 'NONE' and RequestAttributes.allowed_granularity in ['count','record'] and RequestAttributes.qparams.query.requestedGranularity in ['count', 'record']:
        RequestAttributes.response_type = 'count'
    else:
        RequestAttributes.response_type = 'boolean'
    if RequestAttributes.allowed_granularity == 'boolean':
        RequestAttributes.returned_granularity = 'boolean'
    elif RequestAttributes.allowed_granularity in ['count', 'record'] and RequestAttributes.qparams.query.requestedGranularity == 'boolean':
        RequestAttributes.returned_granularity = 'boolean'
    elif RequestAttributes.allowed_granularity == 'record' and RequestAttributes.qparams.query.requestedGranularity == 'record' and RequestAttributes.response_type == 'resultSet':
        RequestAttributes.returned_granularity = 'record'
    else:
        RequestAttributes.returned_granularity = 'count'
    if RequestAttributes.entry_type not in ['filtering_terms', 'map', 'configuration', 'info', 'service-info', 'entry_types']:
        if RequestAttributes.entry_type == endpoint_module.endpoint_name:
            if endpoint_module.allow_queries_without_filters == False and RequestAttributes.qparams.query.filters == [] and RequestAttributes.qparams.query.requestParameters == {}:
                raise NoFiltersAllowed("{} endpoint doesn't allow query without filters".format(RequestAttributes.entry_type))

    if RequestAttributes.qparams.meta.apiVersion in os.listdir("/beacon/framework"):
        RequestAttributes.returned_apiVersion = RequestAttributes.qparams.meta.apiVersion
    else:
        RequestAttributes.returned_apiVersion = api_version
    if RequestAttributes.qparams.meta.requestedSchemas != []:
        for schema in RequestAttributes.qparams.meta.requestedSchemas:
            if RequestAttributes.entry_type == endpoint_module.endpoint_name:
                if schema == endpoint_module.defaultSchema_id:
                    RequestAttributes.returned_schema = [SchemasPerEntity(entityType=endpoint_module.id,schema=schema).model_dump()]
                elif schema in endpoint_module.aditionally_supported_schemas:
                    RequestAttributes.returned_schema = [SchemasPerEntity(entityType=endpoint_module.id,schema=schema).model_dump()]
                else:
                    RequestAttributes.returned_schema = [SchemasPerEntity(entityType=endpoint_module.id,schema=endpoint_module.defaultSchema_id).model_dump()]
    elif RequestAttributes.entry_type not in ['filtering_terms', 'map', 'configuration', 'info', 'service-info', 'entry_types']:
        if RequestAttributes.entry_type == endpoint_module.endpoint_name:
            RequestAttributes.returned_schema = [SchemasPerEntity(entityType=endpoint_module.id,schema=endpoint_module.defaultSchema_id).model_dump()]
    if RequestAttributes.entry_type == 'filtering_terms':
        RequestAttributes.returned_schema = {"schema": "filtering_terms-{}".format(RequestAttributes.returned_apiVersion)}
    elif RequestAttributes.entry_type == 'map':
        RequestAttributes.returned_schema = {"schema": "map-{}".format(RequestAttributes.returned_apiVersion)}
    elif RequestAttributes.entry_type == 'configuration':
        RequestAttributes.returned_schema = {"schema": "configuration-{}".format(RequestAttributes.returned_apiVersion)}
    elif RequestAttributes.entry_type == 'info':
        RequestAttributes.returned_schema = {"schema": "info-{}".format(RequestAttributes.returned_apiVersion)}
    elif RequestAttributes.entry_type == 'service-info':
        RequestAttributes.returned_schema = {"schema": "service-info-{}".format(RequestAttributes.returned_apiVersion)}
    elif RequestAttributes.entry_type == 'entry_types':
        RequestAttributes.returned_schema = {"schema": "entry_types-{}".format(RequestAttributes.returned_apiVersion)}

@log_with_args(level)
def set_ip(self, request):
    RequestAttributes.ip=request.remote

@log_with_args(level)
def set_headers(self, request):
    RequestAttributes.headers=request.headers

    
@log_with_args(level)
async def deconstruct_request(self, request):
    '''
    Here we grab the attributes that come from a request: ip, headers, entry_type related attributes and request parameters in four different steps, the order of which is
    declared first is not relevant.
    '''
    set_ip(self, request)
    set_headers(self, request)
    set_entry_type(self, request)
    await get_qparams(self, self.request)
    set_response_type(self)