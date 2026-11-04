from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import json

def audit_check(func):
    @log_with_args(config.level)
    async def wrapper(self, *args, **kwargs):

        self.LOG.warning('audit func is applied')

        audit_response={}
        
        self.LOG.warning(self.request_attributes.qparams)

        audit_response["request_id"]=self._id

        audit_response["request"]={}

        audit_response["request"]["method"]=self.request.method

        audit_response["request"]["path"]=self.request.path_qs

        audit_response["request"]["route"]=config.uri_subpath+'/'+self.request_attributes.entry_type

        path_parameters=self.request.path_qs.split('?')

        if len(path_parameters)>1:
            path_parameters=path_parameters[1]

            path_parameters_list=path_parameters.split('&')

            audit_response["request"]["path_parameters"]={}

            for path_parameter in path_parameters_list:
                path_parameter_splitted=path_parameter.split('=')
                audit_response["request"]["path_parameters"][path_parameter_splitted[0]]=path_parameter_splitted[1]
        else:
            path_parameters={}
            audit_response["request"]["path_parameters"]={}

        audit_response["request"]["headers"]=dict(self.request.headers)

        audit_response["request"]["http_version"]=f"{self.request.version.major}.{self.request.version.minor}"

        audit_response["request"]["client"]={}

        audit_response["request"]["client"]["ip"]=self.request.remote

        audit_response["request"]["client"]["user_agent"]=self.request.headers['User-Agent']

        audit_response["request"]["body"]={}

        audit_response["request"]["body"]["present"]=True if self.request.has_body else False

        if self.request.has_body:
            body = json.dumps(await self.request.json()).encode("utf-8")
            body_size = len(body)
            audit_response["request"]["body"]["size_bytes"]=body_size
        else:
            audit_response["request"]["body"]["size_bytes"]=0

        for header in ("Content-MD5", "Digest", "Content-Digest"):
            values = self.request.headers.getall(header, [])
            if values:
                audit_response["request"]["body"]["content_hash"]=values

        audit_response["request"]["identity"]=""

        self.LOG.warning(audit_response)

        result = await func(self, *args, **kwargs)

        return result

    return wrapper