
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.request.classes import ErrorClass
import html

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
async def get_qparams(self, post_data, request):
    try:
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
                catch_query["query"]["skip"] = v
            elif k == 'limit':
                catch_query["query"]["limit"] = v
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
            post_data["query"]=catch_query["query"]
        if catch_query_params!={}:
            try:
                for k, v in catch_query_params.items():
                    try:
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
        if post_data is not None:
            qparams = RequestParams(**post_data).from_request(post_data)
        else:
            json_body={}
            qparams = RequestParams(**post_data).from_request(post_data)
        return qparams
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=400
        ErrorClass.error_message='set of meta/query parameters: {} not allowed'.format(post_data)
        raise web.HTTPBadRequest