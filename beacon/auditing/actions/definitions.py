
from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticAction:

    action: str
    resource_type: str
    description: str
    category: str


# ---------------------------------------------------------
# DATA RESOURCE ACTIONS
# ---------------------------------------------------------

RESOURCE_ACTIONS = {

    "analyses": SemanticAction(
        "analysis.query",
        "analysis",
        "Query analyses",
        "data_access"
    ),

    "biosamples": SemanticAction(
        "biosample.query",
        "biosample",
        "Query biosamples",
        "data_access"
    ),

    "cohorts": SemanticAction(
        "cohort.query",
        "cohort",
        "Query cohorts",
        "data_access"
    ),

    "individuals": SemanticAction(
        "individual.query",
        "individual",
        "Query individuals",
        "data_access"
    ),

    "genomicVariants": SemanticAction(
        "genomic_variant.query",
        "genomic_variant",
        "Query genomic variants",
        "data_access"
    ),

    "runs": SemanticAction(
        "run.query",
        "run",
        "Query runs",
        "data_access"
    ),

    "datasets": SemanticAction(
        "dataset.query",
        "dataset",
        "Query datasets",
        "data_access"
    ),

    "patients": SemanticAction(
        "patient.query",
        "patient",
        "Query patients",
        "data_access"
    ),

    "collections": SemanticAction(
        "collection.query",
        "collection",
        "Query collections",
        "data_access"
    ),
}


# ---------------------------------------------------------
# FRAMEWORK ACTIONS
# ---------------------------------------------------------

FRAMEWORK_ACTIONS = {

    "": SemanticAction(
        "service.info",
        "service",
        "Retrieve service information",
        "system"
    ),

    "info": SemanticAction(
        "service.info",
        "service",
        "Retrieve service information",
        "system"
    ),

    "entry_types": SemanticAction(
        "metadata.entry_types.list",
        "metadata",
        "List available entry types",
        "configuration"
    ),

    "service-info": SemanticAction(
        "service.info",
        "service",
        "Retrieve service information",
        "system"
    ),

    "configuration": SemanticAction(
        "configuration.view",
        "configuration",
        "Retrieve service configuration",
        "configuration"
    ),

    "map": SemanticAction(
        "metadata.map.view",
        "metadata",
        "Retrieve Beacon map",
        "configuration"
    ),

    "filtering_terms": SemanticAction(
        "metadata.filtering_terms.list",
        "metadata",
        "Retrieve filtering terms",
        "configuration"
    ),

    "health": SemanticAction(
        "system.health.check",
        "system",
        "Check service health",
        "health"
    ),
}


# ---------------------------------------------------------
# INTERNAL SYSTEM ACTIONS
# ---------------------------------------------------------

SYSTEM_ACTIONS = {

    # Authentication

    "authentication.success": SemanticAction(
        "authentication.success",
        "authentication",
        "Authentication succeeded",
        "authentication"
    ),

    "authentication.failed": SemanticAction(
        "authentication.failed",
        "authentication",
        "Authentication failed",
        "authentication"
    ),

    # Authorization

    "authorization.evaluate": SemanticAction(
        "authorization.evaluate",
        "authorization",
        "Authorization evaluated",
        "authorization"
    ),

    "authorization.granted": SemanticAction(
        "authorization.granted",
        "authorization",
        "Authorization granted",
        "authorization"
    ),

    "authorization.denied": SemanticAction(
        "authorization.denied",
        "authorization",
        "Authorization denied",
        "authorization"
    ),

    # Query budget

    "budget.evaluate": SemanticAction(
        "budget.evaluate",
        "budget",
        "Query budget evaluated",
        "budget"
    ),

    "budget.accepted": SemanticAction(
        "budget.accepted",
        "budget",
        "Query budget accepted",
        "budget"
    ),

    "budget.rejected": SemanticAction(
        "budget.rejected",
        "budget",
        "Query budget rejected",
        "budget"
    ),

    # Database

    "database.connection.select": SemanticAction(
        "database.connection.select",
        "database",
        "Database connection selected",
        "database"
    ),

    "database.health.check": SemanticAction(
        "database.health.check",
        "database",
        "Database health checked",
        "health"
    ),

    "database.operation": SemanticAction(
        "database.operation",
        "database",
        "Database operation executed",
        "database"
    ),

    # Response processing

    "response.validate": SemanticAction(
        "response.validate",
        "response",
        "Response validation performed",
        "system"
    ),

    "response.serialize": SemanticAction(
        "response.serialize",
        "response",
        "Response serialization performed",
        "system"
    ),

    # Audit processing

    "audit.persist": SemanticAction(
        "audit.persist",
        "audit",
        "Audit record persisted",
        "administration"
    ),

    "audit.integrity.verify": SemanticAction(
        "audit.integrity.verify",
        "audit",
        "Audit integrity verified",
        "administration"
    ),
}
