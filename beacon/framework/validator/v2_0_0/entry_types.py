from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    create_model
)
import re
from typing import List, Optional
from beacon.utils.modules import load_class, get_modules_confiles

class OntologyTerm(BaseModel):
    """
    Represents a controlled vocabulary term using a CURIE-style identifier.

    Example:
        NCIT:C42331
    """

    id: str
    label: Optional[str] = None

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        """
        Validate that the ontology identifier follows CURIE format.

        CURIE format expected:
        - prefix:alphanumeric_id (e.g. NCIT:C42331)
        """

        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')

        return v


class EntryTypes(BaseModel):
    """
    Describes metadata for an entry type in the Beacon configuration.

    Each entry type defines:
    - Schema definitions
    - Supported query behavior
    - Ontology mapping
    """

    aCollectionOf: Optional[List] = None

    # Additional schema definitions supported for this entry type
    additionallySupportedSchemas: Optional[List[
        load_class("common", "ReferenceToAnSchema")
    ]] = None

    # Default schema definition for this entry type
    defaultSchema: load_class("common", "ReferenceToAnSchema")

    description: Optional[str] = None

    # Unique identifier for the entry type
    id: str

    # Human-readable name
    name: str

    # Whether queries without filters are allowed
    nonFilteredQueriesAllowed: Optional[bool] = True

    # Ontology term describing this entry type
    ontologyTermForThisType: Optional[OntologyTerm] = None

    # Specification section this entry type belongs to
    partOfSpecification: str


# ------------------------------------------------------------
# Dynamically generate entry type fields from configuration
# ------------------------------------------------------------

list_of_modules = get_modules_confiles()

fields_related = {
    str(key): (Optional[EntryTypes], None)
    for field_name in list_of_modules
    for key, value in field_name.items()
}

# Dynamically constructed Pydantic model containing all entry types
Entries = create_model("Entries", **fields_related)

# External schema reference model
ReferenceToAnSchema = load_class("common", "ReferenceToAnSchema")


class Entries(Entries):
    """
    Wrapper model enforcing global constraints on all entry types.

    Ensures at least one entry type is configured.
    """

    @model_validator(mode="before")
    def at_least_one_not_none(cls, values):
        # Ensure system is not initialized with zero active entry types
        if not any(value is not None for value in values.values()):
            raise ValueError("At least one entry type must be active for the beacon")

        return values


class EntryTypesSchema(BaseModel):
    """
    Full schema builder for all entry types in the system.

    This class dynamically constructs entry type definitions
    based on configuration modules.
    """

    entryTypes: Entries

    def return_schema(self):
        """
        Build full EntryTypes schema dynamically from configuration.

        This method:
        - Reads module configuration
        - Builds EntryTypes objects per entry
        - Attaches ontology metadata
        - Adds default and supported schemas
        - Returns validated Pydantic structure
        """

        # Container for constructed entry type definitions
        Entries_values_to_Set = {}

        # ------------------------------------------------------------
        # Iterate over configured modules and entry types
        # ------------------------------------------------------------
        for module in list_of_modules:
            for entry_type, set_of_params in module.items():

                # Temporary dictionary for entry type attributes
                values_to_set = {}

                # Only include enabled entry types
                if set_of_params["entry_type_enabled"] == True:

                    # Basic identity metadata
                    values_to_set["id"] = entry_type
                    values_to_set["name"] = set_of_params["info"]["name"]

                    # Ontology mapping for entry type classification
                    values_to_set["ontologyTermForThisType"] = OntologyTerm(
                        id=set_of_params["info"]["ontology_id"],
                        label=set_of_params["info"]["ontology_name"]
                    )

                    # Specification grouping
                    values_to_set["partOfSpecification"] = set_of_params["schema"]["specification"]

                    # Human-readable description
                    values_to_set["description"] = set_of_params["info"]["description"]

                    # Default schema definition
                    values_to_set["defaultSchema"] = ReferenceToAnSchema(
                        id=set_of_params["schema"]["default_schema_id"],
                        name=set_of_params["schema"]["default_schema_name"],
                        referenceToSchemaDefinition=set_of_params["schema"]["reference_to_default_schema_definition"],
                        schemaVersion=set_of_params["schema"]["default_schema_version"]
                    )

                    # --------------------------------------------------------
                    # Build list of supported schemas
                    # --------------------------------------------------------
                    list_of_supported_schemas = []

                    for supported_schema in set_of_params["schema"]["supported_schemas"]:
                        list_of_supported_schemas.append(
                            ReferenceToAnSchema(
                                id=supported_schema,
                                name=supported_schema,
                                referenceToSchemaDefinition=set_of_params["schema"]["reference_to_default_schema_definition"]
                            )
                        )

                    values_to_set["additionallySupportedSchemas"] = list_of_supported_schemas

                    # Whether queries without filters are allowed
                    values_to_set["nonFilteredQueriesAllowed"] = set_of_params["allow_queries_without_filters"]

                    # Store constructed entry type
                    Entries_values_to_Set[entry_type] = values_to_set

        # ------------------------------------------------------------
        # Final model construction
        # ------------------------------------------------------------
        if Entries_values_to_Set != {}:
            entryTypes_values_to_set = Entries(**Entries_values_to_Set)
        else:
            entryTypes_values_to_set = None

        # Return final schema instance
        return self(entryTypes=entryTypes_values_to_set)


class EntryTypesResponse(BaseModel):
    """
    API response wrapper for entry type schema endpoint.

    Combines metadata and dynamically generated entry type schema.
    """

    meta: load_class("meta", "InformationalMeta")
    response: EntryTypesSchema