from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_source_module, load_framework_module

class FilteringTermsView(EndpointView):
    @log_with_args(config.level)
    async def handler(self):
        # Load the module that owns the source where filtering terms are located at and get the class filled with the filtering terms data of the response
        module = load_source_module(self, 'filtering_terms')
        ftResponseClass = module.get_filtering_terms(self)
        # Load the modules that will serve as the meta and the fitering terms part of the response
        module_meta = load_framework_module(self, "meta")
        module_filtering_terms = load_framework_module(self, "filtering_terms")
        try:
            # Generate the class for the filtering terms results and load it with the docs returned from the filtering terms source
            filteringterms = module_filtering_terms.FilteringTermsResults(filteringTerms=ftResponseClass.docs)
            # Generate the Meta class for the meta part of the response and populate it with data from the configuration
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            # Create the response class that will allocate both Meta and Filtering Terms parts of the response
            self.classResponse = module_filtering_terms.FilteringTermsResponse(meta=meta.model_dump(exclude_none=True),response=filteringterms.model_dump(exclude_none=True))
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')