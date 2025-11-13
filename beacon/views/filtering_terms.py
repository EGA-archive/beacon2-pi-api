from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_source_module

class FilteringTermsView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        module = load_source_module(self, 'filtering_terms')
        ftResponseClass = module.get_filtering_terms(self)
        meta_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.meta'
        filtering_terms_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.filtering_terms'
        import importlib
        module_meta = importlib.import_module(meta_module, package=None)
        module_filtering_terms = importlib.import_module(filtering_terms_module, package=None)
        try:
            filteringterms = module_filtering_terms.FilteringTermsResults(filteringTerms=ftResponseClass.docs)
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = module_filtering_terms.FilteringTermsResponse(meta=meta.model_dump(exclude_none=True),response=filteringterms.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')