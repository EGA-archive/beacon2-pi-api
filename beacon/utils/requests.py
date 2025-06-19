
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level, uri, uri_subpath
from beacon.request.classes import ErrorClass, RequestAttributes
import html
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run

@log_with_args(level)
async def check_request_content_type(self, request: Request):
    try:# pragma: no cover
        if request.headers.get('Content-Type') == 'application/json':
            post_data = await request.json()
        else:
            post_data = await request.post()
        return post_data
    except Exception:# pragma: no cover
        raise


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
                v_list =v.split(',')# pragma: no cover
            else:
                v_list.append(v)
            for id in v_list:
                v_dict={}
                v_dict['id']=id
            query_string_body["query"]["filters"] = [v_dict]
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
            query_string_body["meta"]["requestedSchemas"] = v
        elif k == 'requestedGranularity':
            query_string_body["query"]["requestedGranularity"] = v
        elif k == 'datasets':
            query_string_body["query"]["requestParameters"][k]=[v]
        elif k in ["start", "end"]:
            if ',' in v:# pragma: no cover
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
        post_data = await request.json() if request.has_body else {}
        try:
            if post_data["query"]["requestParameters"] == {}:
                ErrorClass.error_message='requestParameters can not be empty, remove the requestParameters property from the body if you do not want to apply any'
        except Exception:
            pass
        query_string_body = parse_query_string(self, request)
        final_body=post_data
        for k, v in query_string_body.items():
            if post_data.get(k) == None:
                final_body[k]=v
            else:
                for k1, v1 in v.items():
                    if post_data[k].get(k1)==None:
                        final_body[k][k1]=v1
                    elif isinstance(v1, dict):
                        for k2, v2 in v1.items():
                            if post_data[k][k1].get(k2)==None:
                                final_body[k][k1][k2]=v2
                            elif isinstance(v2, list):
                                if post_data[k][k1][k2]!=v2:
                                    ErrorClass.error_message='two parameters conflict from string: {} and from json body query: {}'.format(v2, post_data[k][k1][k2])
                                    raise web.HTTPBadRequest
                            elif isinstance(v2, dict):
                                for k3, v3 in v2.items():
                                    if post_data[k][k1][k2].get(k3)==None:
                                        final_body[k][k1][k2][k3]=v3
                                    elif post_data[k][k1][k2][k3]!=v3:
                                        ErrorClass.error_message='two parameters conflict from string: {} and from json body query: {}'.format(v3, post_data[k][k1][k2][k3])
                                        raise web.HTTPBadRequest
                            elif post_data[k][k1][k2]!=v2:
                                ErrorClass.error_message='two parameters conflict from string: {} and from json body query: {}'.format(v2, post_data[k][k1][k2])
                                raise web.HTTPBadRequest
                    elif post_data[k][k1]!=v1:
                        ErrorClass.error_message='two parameters conflict from string: {} and from json body query: {}'.format(v1, post_data[k][k1])
                        raise web.HTTPBadRequest
        qparams = RequestParams(**final_body).from_request(final_body)
        return qparams
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=400
        if ErrorClass.error_message is None:
            ErrorClass.error_message='set of meta/query parameters: {} not allowed'.format(post_data)
        raise web.HTTPBadRequest
    
@log_with_args(level)
def set_entry_type_configuration(self):
    '''
    On the action of checking if there is a match between the endpoint queried an entry type in configuration, we then grab the database (source), max_granularity (allowed_granularity)
    and id name of the records of the entry type to keep them in the RequestAttributes object for later.
    '''
    if RequestAttributes.entry_type == genomicVariant.endpoint_name:
        RequestAttributes.source = genomicVariant.database
        RequestAttributes.allowed_granularity = genomicVariant.granularity
        RequestAttributes.entry_type_id = genomicVariant.id
    elif RequestAttributes.entry_type == analysis.endpoint_name:
        RequestAttributes.source = analysis.database
        RequestAttributes.allowed_granularity = analysis.granularity
        RequestAttributes.entry_type_id = analysis.id
    elif RequestAttributes.entry_type == biosample.endpoint_name:
        RequestAttributes.source = biosample.database
        RequestAttributes.allowed_granularity = biosample.granularity
        RequestAttributes.entry_type_id = biosample.id
    elif RequestAttributes.entry_type == individual.endpoint_name:
        RequestAttributes.source = individual.database
        RequestAttributes.allowed_granularity = individual.granularity
        RequestAttributes.entry_type_id = individual.id
    elif RequestAttributes.entry_type == run.endpoint_name:
        RequestAttributes.source = run.database
        RequestAttributes.allowed_granularity = run.granularity
        RequestAttributes.entry_type_id = run.id
    
@log_with_args(level)
def set_entry_type(self, request):
    '''
    We receive an absolute url with a host and a port, the endpoint queried and the query string. We check that the url and host match with the beacon uri in conf and then
    we keep the name of the endpoint checking if it matches an entry type in configuration and the internal id queried, if there is one.
    '''
    try:
        abs_url_with_query_string=str(request.url)
        abs_url=abs_url_with_query_string.split('?')
        abs_url=abs_url[0]
        if uri.endswith('/'):
            starting_endpoint = len(uri) + len(uri_subpath) -1
            def_uri=uri + uri_subpath
        else:
            starting_endpoint = len(uri) + len(uri_subpath)
            def_uri = uri + uri_subpath
        if abs_url[:starting_endpoint] != def_uri :
            ErrorClass.error_code=400
            if ErrorClass.error_message is None:
                ErrorClass.error_message='configuration variable uri: {} not the same as where the beacon is hosted'.format(uri)
            raise web.HTTPBadRequest
        path_list = abs_url[starting_endpoint:].split('/')
        if len(path_list) > 3:
            RequestAttributes.pre_entry_type=path_list[1]
            RequestAttributes.entry_type=path_list[3]
            set_entry_type_configuration(self)
            RequestAttributes.entry_id=request.match_info.get('id', None)
        else:
            RequestAttributes.entry_type=path_list[1]
            set_entry_type_configuration(self)
            RequestAttributes.entry_id=request.match_info.get('id', None)
    except Exception:
        raise

    
@log_with_args(level)
async def deconstruct_request(self, request):
    '''
    Here we grab the attributes that come from a request: ip, headers, entry_type related attributes and request parameters in four different steps, the order of which is
    declared first is not relevant.
    '''
    # headers, path, query string, body
    # analitzar entry type en una sola funció
    RequestAttributes.ip=request.remote
    RequestAttributes.headers=request.headers
    set_entry_type(self, request)
    qparams = await get_qparams(self, self.request)
    return qparams