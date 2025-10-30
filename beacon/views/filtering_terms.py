from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.validator.framework.meta import InformationalMeta
from beacon.validator.framework.filtering_terms import FilteringTermsResults, FilteringTermsResponse
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import filteringTermsTemplate
from beacon.views.endpoint import EndpointView

class FilteringTermsView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.connections.'+RequestAttributes.source+'.filtering_terms'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        count, records = module.get_filtering_terms(self)
        self.define_final_path(filteringTermsTemplate)
        try:
            filteringterms = FilteringTermsResults(filteringTerms=records)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = FilteringTermsResponse(meta=meta,response=filteringterms)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')