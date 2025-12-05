from typing import Optional, Any
from pydantic import (
    BaseModel,
    model_validator,
    Field,
    create_model
)
from beacon.conf import conf
from beacon.utils.modules import load_class, get_modules_confiles
from beacon.logs.logs import LOG

class RelatedEndpoint(BaseModel):
    returnedEntryType: str
    url: str

# Get all the models conf values of the entry types and assign them as properties in a class called RelatedEndpointEntries

list_of_modules=get_modules_confiles()

fields_related = {str(key): (Optional[RelatedEndpoint],None) for field_name in list_of_modules for key, value in field_name.items() }

RelatedEndpointEntries = create_model("RelatedEndpointEntries", **fields_related)

class RelatedEndpointEntries(RelatedEndpointEntries):

    def merge(self, other: "RelatedEndpointEntries"):
        """Merge another RelatedEndpointEntries object into this one."""
        for field_name in self.model_fields.keys():
            current = getattr(self, field_name)
            incoming = getattr(other, field_name)

            # Rule: If incoming is None → ignore
            if incoming is None:
                continue

            # If current is None, take incoming
            if current is None:
                setattr(self, field_name, incoming)
                continue

            # Both exist → merge recursively if it's a Pydantic model
            if isinstance(current, BaseModel) and isinstance(incoming, BaseModel):
                current_dict = current.model_dump()
                incoming_dict = incoming.model_dump()

                # simple rule: incoming overrides any None values
                merged = {k: incoming_dict.get(k) or current_dict.get(k)
                          for k in current_dict.keys()}

                setattr(self, field_name, current.__class__(**merged))
                continue

            # Otherwise overwrite or define your own custom rule
            setattr(self, field_name, incoming)


class Endpoint(BaseModel):
    endpoints: Optional[RelatedEndpointEntries]=None
    openAPIEndpointsDefinition: Optional[str] = None
    entryType: str
    rootUrl: str
    singleEntryUrl: Optional[str] = None

# Get all the models conf values of the entry types and assign them as properties in a class called EndpointEntries

fields = {str(key): (Optional[Endpoint],None) for field_name in list_of_modules for key, value in field_name.items() }

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
        
        for module in list_of_modules:
            relatedEndpointEntries_values_to_set={}
            for entry_type, set_of_params in module.items():
                values_to_set = {}
                if set_of_params["entry_type_enabled"] == True:
                    values_to_set["returnedEntryType"] = entry_type
                    for lookup_entry_type, lookup_set_of_params in set_of_params["lookups"].items():
                        try:
                            values_to_set["url"] = conf.complete_url+'/'+lookup_set_of_params["endpoint_name"] if lookup_set_of_params["endpoint_enabled"] == True else None
                        except Exception:
                            continue
                        relatedEndpointEntries_values_to_set[lookup_entry_type]=values_to_set
                if relatedEndpointEntries_values_to_set != {}:
                    Endpoints = RelatedEndpointEntries(**relatedEndpointEntries_values_to_set)
                else:
                    Endpoints=None
                # Add the rest of the properties for each of the entry type that is particular to them and doesn't depend on a lookup
                rootUrl=conf.complete_url+'/'+set_of_params["endpoint_name"]
                singleEntryUrl=conf.complete_url+'/'+set_of_params["endpoint_name"]+'/{id}' if set_of_params["allow_id_query"]==True else None
                openAPIEndpointsDefinition=set_of_params["open_api_definition"]
                if set_of_params["entry_type_enabled"] == True:
                    if str(entry_type) not in fields:
                        fields[str(entry_type)]=Endpoint(id=entry_type,openAPIEndpointsDefinition=openAPIEndpointsDefinition,entryType=entry_type,rootUrl=rootUrl,singleEntryUrl=singleEntryUrl,endpoints=Endpoints)
                    else:
                        fields[str(entry_type)].endpoints.merge(Endpoints)
        endpointEntriesClass=EndpointEntries(**fields)
        return self(endpointSets=endpointEntriesClass)

class MapResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: MapSchema