from typing import Optional, Any
from pydantic import (
    BaseModel,
    model_validator,
    Field,
    create_model
)
from beacon.conf import conf
from beacon.utils.modules import load_class
from beacon.utils.modules import get_all_modules_conf
from beacon.logs.logs import LOG

class RelatedEndpoint(BaseModel):
    returnedEntryType: str
    url: str

prelist_of_modules = get_all_modules_conf()

list_of_modules=[x for x in prelist_of_modules if x.id != ""]

fields_related = {str(field_name.id): (Optional[RelatedEndpoint],None) for field_name in list_of_modules}

RelatedEndpointEntries = create_model("RelatedEndpointEntries", **fields_related)

class RelatedEndpointEntries(RelatedEndpointEntries):
    @model_validator(mode="before")
    def at_least_one_not_related_none(cls, values):
        if not any(value is not None for value in values.values()):
            raise ValueError("At least one entry type must be active for the beacon")
        return values


class Endpoint(BaseModel):
    endpoints: Optional[RelatedEndpointEntries]=None
    openAPIEndpointsDefinition: Optional[str] = None
    entryType: str
    rootUrl: str
    singleEntryUrl: Optional[str] = None

fields = {str(field_name.id): (Optional[Endpoint],None) for field_name in list_of_modules}

EndpointEntries = create_model("EndpointEntries", **fields)

class EndpointEntries(EndpointEntries):
    @model_validator(mode="before")
    def at_least_one_not_none(cls, values):
        if not any(value is not None for value in values.values()):
            raise ValueError("At least one entry type must be active for the beacon")
        return values

class MapSchema(BaseModel):
    schema: str = Field(alias="$schema", default="https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconConfigurationSchema.json")
    endpointSets: EndpointEntries
    def populate_endpoints(self):
        # Load all_modules and do a loop per populating EndpointEntries(loaded_module=Endpoint...) and loading the variables _lookup = True by name, getting endpoint_names per each lookup = True.
        fields={}
        for module2 in list_of_modules:
            relatedEndpointEntries_values_to_set={}
            for module in list_of_modules:
                values_to_set = {}
                if module2.enable_endpoint == True:
                    lookup = module.id + "_lookup"
                    values_to_set["returnedEntryType"] = module.id
                    try:
                        values_to_set["url"] = conf.complete_url+'/'+module2.endpoint_name+'/{id}/'+module.endpoint_name if getattr(module2, lookup) == True else None
                    except Exception:
                        continue
                    relatedEndpointEntries_values_to_set[module.id]=values_to_set
                else:
                    relatedEndpointEntries_values_to_set[module.id]=None
            if relatedEndpointEntries_values_to_set != {}:
                Endpoints = RelatedEndpointEntries(**relatedEndpointEntries_values_to_set)
            else:
                Endpoints=None
            rootUrl=conf.complete_url+'/'+module2.endpoint_name
            singleEntryUrl=conf.complete_url+'/'+module2.endpoint_name+'/{id}' if module2.singleEntryUrl==True else None
            openAPIEndpointsDefinition=module2.open_api_endpoints_definition
            id = module2.id
            fields[str(module2.id)]=Endpoint(id=id,openAPIEndpointsDefinition=openAPIEndpointsDefinition,entryType=module2.id,rootUrl=rootUrl,singleEntryUrl=singleEntryUrl,endpoints=Endpoints)
        endpointEntriesClass=EndpointEntries(**fields)
        return self(endpointSets=endpointEntriesClass)

class MapResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: MapSchema