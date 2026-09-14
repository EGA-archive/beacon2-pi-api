import logging
from typing import Optional
from sqlalchemy import select, func, bindparam, distinct, cast, String, and_, or_, text

from beacon.models.omop.connections.postgresql.utilities import RequestParams, DefaultSchemas, basic_query, peek, search_ontologies_bio, MAX_LIMIT
import beacon.models.omop.connections.postgresql.mappings as mappings
from beacon.connections.postgresql_omop.__init__ import client
from beacon.connections.postgresql_omop import get_table

LOG = logging.getLogger(__name__)

def map_domains(domain_id):
    # Domain_id : Table in OMOP
    dictMapping = {
        'Specimen': 'specimen_concept_id',
        'Spec Anatomic Site':'"anatomic_site_concept_id"'
    }
    return dictMapping[domain_id]

async def search_descendants(concept_id):
    vocab_conc_anc = get_table("concept_ancestor", schema="vocabularies")
    records = select(
        vocab_conc_anc.c.descendant_concept_id
    ).where(
        vocab_conc_anc.c.ancestor_concept_id == bindparam("concept_id"))
    async with client.connect() as conn:
        records = await conn.execute(records, {"concept_id": concept_id})
    l_descendants = set()
    for descendant in records:
        l_descendants.add(descendant[0])
        
    return l_descendants

def create_dynamic_filter(filters):
    list_person = []
    for fltr in filters:
        # Default type of filter is ontology
        filterType = 'Ontology'
        # For now there is no Alphanumeric available option
        if fltr[2]:       # If filter has an operator (operator!=None) it is an Alphanumeric filter
            filterType = 'Alphanumeric'
        if ("specimen_concept_id" in fltr[0] or "anatomic_site_concept_id" in fltr[0]):
            variable_name = fltr[0]
            or_block = or_(
                *(text(f"{variable_name} = {concept_id}") for concept_id in fltr[1])
            )
            list_person.append(or_block)

    return list_person

def super_query_count(filters):
    cdm_specimen = get_table("specimen", schema="cdm")
    if not filters:
        where_clause = [True]
    elif isinstance(filters, list):
        where_clause = filters
    else:
        where_clause = [filters]
    query = select(
        func.count(distinct(cdm_specimen.c.specimen_id))
    ).where(
        and_(*where_clause)
    ) 

    return query

def super_query_get(filters, offset, limit):
    cdm_specimen = get_table("specimen", schema="cdm")
    if not filters:
        where_clause = [True]
    elif isinstance(filters, list):
        where_clause = filters
    else:
        where_clause = [filters]
    query = (
        select(cdm_specimen.c.specimen_id)
        .where(and_(*where_clause))
        .limit(limit).offset(offset)
    )

    return query

async def checkFilters(filtersDict, offset, limit, typeQuery):
    vocab_conc = get_table("concept", schema="vocabularies")
    listOfList = []
    dictTableMap = []
    for filt in filtersDict:
        listConcept_id = set()
        operator = None
        value = None
        includeDescendantTerms = True
        # Check query
        # Parse query depend on POST/GET query
        if typeQuery == 'POST':
            if 'includeDescendantTerms' in filt:
                if filt['includeDescendantTerms'] == False:
                    includeDescendantTerms = False
            if 'operator' in filt:
                operator = filt['operator']
                value = filt['value']
                includeDescendantTerms = False
            if 'id' in filt:
                filterId = filt['id']
                #print(filterId)
            else:
                return [], 0
        else: # If GET
            filterId = filt
        vocabulary_id, concept_code = filterId.split(':')
        records = select(
            vocab_conc.c.concept_id, vocab_conc.c.domain_id
        ).where(
            (vocab_conc.c.vocabulary_id == bindparam("vocabulary_id")) & (vocab_conc.c.concept_code == bindparam("concept_code"))
        ) 
        async with client.connect() as conn:
            records = await conn.execute(records, {"vocabulary_id": vocabulary_id, "concept_code": concept_code})
            records = records.mappings().all()
        # Check if records is empty
        res = peek(records)
        if res is None:
            return [], 0
        _, records = res
        for record in records:
            original_concept_id = record["concept_id"]
            domain_id = record["domain_id"]
            listConcept_id.add(original_concept_id)
            # Look in which domains the concept_id belongs
            tableMap=map_domains(domain_id)
            if includeDescendantTerms:
                # Import descendants of the concept_id
                concept_ids= await search_descendants(original_concept_id)
                # Concept_id and descendants in same set()
                listConcept_id = listConcept_id.union(concept_ids)
        dictTableMap.append([tableMap, listConcept_id, operator, value])
    base_filter = create_dynamic_filter(dictTableMap)
    query_count = super_query_count(base_filter)
    count_records = await basic_query(query_count)
    query_get = super_query_get(base_filter, offset, limit)
    records_get = await basic_query(query_get)
    listOfList = [record["specimen_id"] for record in records_get]

    return listOfList, count_records[0]["count_1"]

async def filters(filtersDict, offset, limit):
    if type(filtersDict[0]) is dict:         # If filter is from Post
        listFilters, count = await checkFilters(filtersDict, offset, limit, 'POST')
    else:
        listFilters, count = await checkFilters(filtersDict, offset, limit, 'GET')

    return listFilters, count

#####

def format_query_bio(biosamples):
    list_format = []
    for sample in biosamples:
        dict_biosample =  { 
            "id": str(sample.get("specimen_id", "")),
            "individualId": str(sample.get("person_id", "")),
            "biosampleStatus": {
                "id": sample["disease_status_concept_id"]["id"],
                "label": sample["disease_status_concept_id"]["label"]
            },
            "sampleOriginType": {
                "id" : sample["anatomic_site_concept_id"]["id"],
                "label" : sample["anatomic_site_concept_id"]["label"]
            },
            "collectionMoment": sample.get("specimen_date", ""),
            "collectionDate": sample.get("specimen_datetime", ""),
            "info": {}
            }
        list_format.append(dict_biosample)
        
    return list_format

###

async def get_biosamples(entry_id: Optional[str] = None, qparams: RequestParams = RequestParams()):
    cdm_specimen = get_table("specimen", schema="cdm")
    def normalize_ids(entry_id):
        if entry_id is None:
            return None
        if isinstance(entry_id, list):
            return [int(x) for x in entry_id]
        return [int(entry_id)]
    entry_id = normalize_ids(entry_id)
    orig_entry_id = entry_id

    if qparams.query.pagination.limit == 0:
        qparams.query.pagination.limit = MAX_LIMIT
    if not qparams.query.pagination.limit:
        qparams.query.pagination.limit = 10
    async with client.connect() as conn:
        if qparams.query.filters:
            listIds, count_ids = await filters(qparams.query.filters,
                            offset=qparams.query.pagination.skip,
                            limit=qparams.query.pagination.limit)
            if count_ids == 0:
                return DefaultSchemas.BIOSAMPLES, count_ids, []
            entry_id = listIds
        else:
            if entry_id is None:
                default_query = select(cdm_specimen.c.specimen_id).limit(qparams.query.pagination.limit).offset(qparams.query.pagination.skip)
                result = await conn.execute(default_query)
                entry_id = result.scalars().all()
            elif not isinstance(entry_id, list):
                entry_id = [entry_id]
    
        specimen_ids = entry_id
        bio_samples = []
        
        spcmn_query = select(
            cdm_specimen.c.specimen_id,
            cdm_specimen.c.person_id, 
            cdm_specimen.c.disease_status_concept_id, 
            cdm_specimen.c.anatomic_site_concept_id, 
            cast(cdm_specimen.c.specimen_date, String), 
            cast(cdm_specimen.c.specimen_datetime, String)
        ).where(
            cdm_specimen.c.specimen_id.in_(specimen_ids))

        result = await conn.execute(spcmn_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            bio_samples.append(dict(row))  

        if qparams.query.filters:
            counter = count_ids
        elif orig_entry_id is None:
            counter_query = select(func.count('*')).select_from(cdm_specimen)
            result = await conn.execute(counter_query) 
            counter = result.scalar_one()
        else:
            counter = len(bio_samples)

    docs = await search_ontologies_bio(bio_samples)
    docs = format_query_bio(docs)

    return DefaultSchemas.BIOSAMPLES, counter, docs

async def get_filtering_terms_of_biosample(entry_id: Optional[str], qparams: RequestParams):
    vocab_conc = get_table("concept", schema="vocabularies")
    cdm_specimen = get_table("specimen", schema="cdm")
    
    bio_filters = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id,':',vocab_conc.c.concept_code)),
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_specimen,
            (cdm_specimen.c.disease_status_concept_id == vocab_conc.c.concept_id) |
            (cdm_specimen.c.anatomic_site_concept_id == vocab_conc.c.concept_id)))
    
    async with client.connect() as conn:
        bio_filters = await conn.execute(bio_filters, {"entry_id": entry_id})

    l_bioFilters = []
    for filters in bio_filters:
        dict_filter = {"id":filters[0],"label":filters[1],"scopes":["biosample"],"type":"ontology"}
        l_bioFilters.append(dict_filter)
    return DefaultSchemas.FILTERINGTERMS, len(l_bioFilters), l_bioFilters