
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
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
async def get_qparams(self, post_data, request): # anomenar query string en comptes de qparams
    # Bad Request not priority
    '''
    The function will catch all the parameters in the query string and see if they also exist in a json body of the request. If a parameter is found in both places, the json body will
    have priority over the parameter string. After that, the params request will be validated against a pydantic class RequestParams and an instance of the object class will be 
    returned to have a variable called qparams with the query parameters that will be used for processing the query.
    '''
    try:
        try:
            if post_data["query"]["requestParameters"] == {}:
                ErrorClass.error_message='requestParameters can not be empty, remove the requestParameters property from the body if you do not want to apply any'
        except Exception:
            pass
        catch_query_params={}
        catch_query={}
        catch_query["query"]={}
        catch_meta={}
        catch_meta["meta"]={}
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
                catch_query["query"]["filters"] = [v_dict]
            elif k == 'includeResultsetResponses':
                catch_query["query"]["includeResultsetResponses"] = v
            elif k == 'skip':
                try:
                    catch_query["query"]["pagination"]["skip"] = v
                except Exception:
                    catch_query["query"]["pagination"]= {}
                    catch_query["query"]["pagination"]["skip"] = v
            elif k == 'limit':
                try:
                    catch_query["query"]["pagination"]["limit"] = v
                except Exception:
                    catch_query["query"]["pagination"]= {}
                    catch_query["query"]["pagination"]["limit"] = v
            elif k == 'testMode':
                catch_query["query"]["testMode"] = v
            elif k == 'requestedSchemas':
                catch_meta["meta"]["requestedSchemas"] = v
            elif k == 'requestedGranularity':
                catch_query["query"]["requestedGranularity"] = v
            elif k == 'datasets':
                catch_query_params[k]=[v]
            elif k in ["start", "end"]:
                if ',' in v:# pragma: no cover
                    v_splitted = v.split(',')
                    catch_query_params[k]=[int(v) for v in v_splitted]
                else:
                    catch_query_params[k]=[int(v)]
            else:
                catch_query_params[k]=v
        if catch_meta["meta"]!={}:
            post_data["meta"]=catch_meta["meta"]
        if catch_query["query"]!={}:
            if post_data.get('query') != None:
                for k, v in post_data["query"].items():
                    if post_data["query"].get(k) == None:
                        post_data["query"][k]=v
                    elif k == 'filters':
                        for item in v:
                            post_data["query"]["filters"].append(v)
            else:
                post_data["query"]=catch_query["query"]
        if catch_query_params!={}:
            try:
                for k, v in catch_query_params.items():
                    try:
                        if post_data["query"]["requestParameters"].get(k) == None:
                            post_data["query"]["requestParameters"][k]=v
                    except Exception:
                        try:
                            post_data["query"]["requestParameters"]={}
                            post_data["query"]["requestParameters"][k]=v
                        except Exception:
                            post_data["query"]={}
                            post_data["query"]["requestParameters"]={}
                            post_data["query"]["requestParameters"][k]=v
            except Exception:
                if catch_query != {}:
                    post_data["query"]["requestParameters"]=catch_query_params 
                else:
                    post_data["query"]={}
                    post_data["query"]["requestParameters"]=catch_query_params
        

        qparams = RequestParams(**post_data).from_request(post_data)
        return qparams
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=400
        if ErrorClass.error_message is None:
            ErrorClass.error_message='set of meta/query parameters: {} not allowed'.format(post_data)
        raise web.HTTPBadRequest
    
@log_with_args(level)
async def deconstruct_request(self, request):
        ip = request.remote
        RequestAttributes.ip=ip
        post_data = await request.json() if request.has_body else {}
        headers = request.headers
        RequestAttributes.headers=headers
        path_list = request.path.split('/')
        if len(path_list) > 4:
            entry_type=path_list[2]+'.'+path_list[4]# pragma: no cover
        else:
            entry_type=path_list[2]
        RequestAttributes.entry_type=entry_type
        entry_id = request.match_info.get('id', None)
        if entry_id == None:
            entry_id = request.match_info.get('variantInternalId', None)
        RequestAttributes.entry_id=entry_id
        if '.' in RequestAttributes.entry_type and genomicVariant.endpoint_name not in RequestAttributes.entry_type:
            source_entry_type = RequestAttributes.entry_type.split('.')
            source_entry_type = source_entry_type[1]
            if source_entry_type == analysis.endpoint_name:
                RequestAttributes.source = analysis.database
                RequestAttributes.allowed_granularity = analysis.granularity
                RequestAttributes.entry_type_id = analysis.id
            elif source_entry_type == biosample.endpoint_name:
                RequestAttributes.source = biosample.database
                RequestAttributes.allowed_granularity = biosample.granularity
                RequestAttributes.entry_type_id = biosample.id
            elif source_entry_type == individual.endpoint_name:
                RequestAttributes.source = individual.database
                RequestAttributes.allowed_granularity = individual.granularity
                RequestAttributes.entry_type_id = individual.id
            elif source_entry_type == run.endpoint_name:
                RequestAttributes.source = run.database
                RequestAttributes.allowed_granularity = run.granularity
                RequestAttributes.entry_type_id = run.id
        elif RequestAttributes.entry_type == genomicVariant.endpoint_name:
            RequestAttributes.source = genomicVariant.database
            RequestAttributes.allowed_granularity = genomicVariant.granularity
            RequestAttributes.entry_type_id = genomicVariant.id
        elif '.' in RequestAttributes.entry_type:
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
        qparams = await get_qparams(self, post_data, self.request)
        return qparams