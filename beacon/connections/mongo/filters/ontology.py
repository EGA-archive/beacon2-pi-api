from beacon.request.parameters import OntologyFilter
from beacon.request.classes import Similarity
from beacon.connections.mongo.utils import get_documents, choose_scope
from beacon.connections.mongo.__init__ import filtering_terms, similarities, synonyms as synonyms_
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.utils.modules import get_all_modules_mongo_connections_script

@log_with_args(config.level)
def apply_ontology_filter(self, query: dict, filter: OntologyFilter, request_parameters: dict, dataset: str) -> dict:
    # Search for synonyms in the query filter
    final_term_list=[]    
    query_synonyms={}
    query_synonyms['id']=filter.id
    synonyms=get_documents(self,
        synonyms_,
        query_synonyms,
        0,
        1
    )
    try:
        synonym_id=synonyms[0]['synonym']
    except Exception:
        synonym_id=None
    if synonym_id is not None:
        final_term_list.append(synonym_id)

    try:
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
    except Exception:
        if synonym_id is not None:
            filter.id=synonym_id
            scope = filter.scope
            scope=choose_scope(self, scope, filter)
        else:
            raise

    # Search similar
    if filter.similarity != Similarity.EXACT:
        try:
            if filter.similarity == Similarity.HIGH:
                ontology_dict=similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_high"]
            elif filter.similarity == Similarity.MEDIUM:
                ontology_dict=similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_medium"]
            elif filter.similarity == Similarity.LOW:
                ontology_dict=similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_low"]
        except Exception:
            pass
        
    # Apply descendant terms
    if filter.includeDescendantTerms == True:
        ontology=filter.id.replace("\n","")
        list_descendant = []
        try:
            ontology_dict=similarities.find({"id": ontology})
            list_descendant = ontology_dict[0]["descendants"]
            for descendant in list_descendant:
                final_term_list.append(descendant)
        except Exception:
            pass
    final_term_list.append(filter.id)

    # Create the query syntax for the filtering term to match the field with the ontology label
    query_filtering={}
    query_filtering['$and']=[]
    dict_id={}
    dict_id['id']=filter.id
    dict_scope={}
    dict_scope['scopes']=scope
    query_filtering['$and'].append(dict_id)
    query_filtering['$and'].append(dict_scope)
    docs = get_documents(self,
        filtering_terms,
        query_filtering,
        0,
        1
    )

    for doc_term in docs:
        label = doc_term['label']
    
    # Get the alphanumeric pair of the ontology filtering term
    query_filtering={}
    query_filtering['$and']=[]
    dict_regex={}
    try:
        dict_regex['$regex']=":"+label
        dict_regex['$options']='i'
    except Exception:
        dict_regex['$regex']=''
    dict_id={}
    dict_id['id']=dict_regex
    dict_scope={}
    dict_scope['scopes']=scope
    query_filtering['$and'].append(dict_id)
    query_filtering['$and'].append(dict_scope)
    docs_2 = get_documents(self,
        filtering_terms,
        query_filtering,
        0,
        1
    )

    # Extract the field/property to look at
    for doc2 in docs_2:
        query_terms = doc2['id']
        query_terms = query_terms.split(':')
        query_term = query_terms[0] + '.id'
    
    # Generate the filter
    if final_term_list !=[]:
        new_query={}
        query_id={}
        new_query['$or']=[]
        for simil in final_term_list:
            query_id={}
            query_id[query_term]=simil
            new_query['$or'].append(query_id)
        query = new_query
    # Execute the cross query in case it's needed
    list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
    for module in list_modules:
        query = module.cross_query(self, query, scope, request_parameters, dataset)
    return query