
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.request.classes import ErrorClass

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
    LOG.debug(request)
    if post_data is not None:
        qparams = RequestParams(**post_data).from_request(request)
    else:
        json_body={}
        qparams = RequestParams(**json_body).from_request(request)
    LOG.debug(qparams)
    return qparams
    '''
    except Exception as e:# pragma: no cover
        catch_req_params = {}
        for k, v in request.items():
            catch_req_params[k]=v
        ErrorClass.error_code=400
        ErrorClass.error_message='set of meta/query parameters: {} not allowed'.format(catch_req_params)
        raise web.HTTPBadRequest
    '''