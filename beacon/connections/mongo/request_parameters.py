from beacon.request.parameters import RequestParams, AlphanumericFilter, Operator
from typing import List, Dict
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from aiohttp import web
from beacon.connections.mongo.filters import apply_alphanumeric_filter
from beacon.connections.mongo.__init__ import client

VARIANTS_PROPERTY_MAP = {
    "start": "variation.location.interval.start.value",
    "end": "variation.location.interval.end.value",
    "assemblyId": "identifiers.genomicHGVSId",
    "referenceName": "identifiers.genomicHGVSId",
    "referenceBases": "variation.referenceBases",
    "alternateBases": "variation.alternateBases",
    "variantType": "variation.variantType",
    "variantMinLength": "variantInternalId",
    "variantMaxLength": "variantInternalId",
    "geneId": "molecularAttributes.geneIds",
    "genomicAlleleShortForm": "identifiers.genomicHGVSId",
    "aminoacidChange": "molecularAttributes.aminoacidChanges",
    "clinicalRelevance": "caseLevelData.clinicalInterpretations.clinicalRelevance",
    "mateName": "identifiers.genomicHGVSId"
}

@log_with_args(level)
def generate_position_filter_start(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.GREATER_EQUAL
        ))
    elif len(value) == 2:# pragma: no cover
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.GREATER_EQUAL
        ))
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[1],
            operator=Operator.LESS_EQUAL
        ))
    return filters


@log_with_args(level)
def generate_position_filter_end(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.LESS
        ))
    elif len(value) == 2:# pragma: no cover
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.GREATER_EQUAL
        ))
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[1],
            operator=Operator.LESS_EQUAL
        ))
    return filters

@log_with_args(level)
def generate_position_filter_start_sequence_query(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.EQUAL
        ))
    return filters



@log_with_args(level)
def apply_request_parameters(self, query: Dict[str, List[dict]], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    if len(qparams.query.requestParameters) > 0 and "$and" not in query:
        query["$and"] = []
    subquery={}
    subquery["$and"] = []
    subqueryor={}
    subqueryor["$or"] = []
    referencedict={}
    referencedict["$or"] = []
    startquery={}
    startquery["$and"]=[]
    startrangequery={}
    startrangequery["$and"]=[]
    endquery={}
    endquery["$and"]=[]
    length_query={}
    length_query["$and"]=[]
    equal=False
    isBracket=False
    for k, v in qparams.query.requestParameters.items():
        if k == 'end':
            equal=True
            endvalue=v
        if k == 'start':
            startvalue=v
    for k, v in qparams.query.requestParameters.items():
        if k == "start":
            if isinstance(v, str):
                v = v.split(',')
                if len(v)>1:
                    isBracket=True
            elif isinstance(v, list) and len(v) > 1:
                isBracket=True
            if equal == False:
                filters = generate_position_filter_start_sequence_query(self, k, v)
                for filter in filters:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset, True))
            elif isBracket == True:
                filters = generate_position_filter_start(self, k, v)
                for filter in filters:
                    startdictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    startquery["$and"].append(startdictvalue)
            else:
                startvalue=v
                if isinstance(startvalue, list):
                    finalvalue=str(0)+','+str(startvalue[0]-1)
                else:
                    finalvalue=str(0)+','+str(startvalue-1)
                finalvalue = finalvalue.split(',')
                filters = generate_position_filter_start(self, k, finalvalue)
                for filter in filters:
                    startdictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    length_query["$and"].append(startdictvalue)
                if isinstance(endvalue, list) and isinstance(startvalue, list):
                    finalvalue=str(startvalue[0])+','+str(endvalue[0])
                if isinstance(startvalue, list):
                    finalvalue=str(startvalue[0])+','+str(endvalue[0])
                elif isinstance(endvalue, list):
                    finalvalue=str(startvalue)+','+str(endvalue[0])
                else:
                    finalvalue=str(startvalue)+','+str(endvalue)
                finalvalue = finalvalue.split(',')
                filters = generate_position_filter_start(self, k, finalvalue)
                for filter in filters:
                    startdict=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    startrangequery["$and"].append(startdict)  
                subqueryor["$or"].append(startrangequery)            
        elif k == "end":
            if isinstance(v, str):
                v = v.split(',')
                if len(v)>1:
                    isBracket=True
            elif isinstance(v, list) and len(v) > 1:
                isBracket=True
            filters = generate_position_filter_end(self, k, v)
            if isBracket==True:
                for filter in filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    startquery["$and"].append(enddictvalue)
                query["$and"].append(startquery)    
            elif isBracket==False:
                if isinstance(v, list) and isinstance(startvalue, list):
                    startvalue=startvalue[0]
                    v = str(v[0])
                    stage2v = str(startvalue)+','+v
                elif isinstance(v, list):
                    v = str(v[0])
                    stage2v = str(startvalue)+','+v
                elif isinstance(startvalue, list):
                    startvalue=startvalue[0]
                    stage2v = str(startvalue)+','+str(v)
                else:
                    stage2v = str(startvalue)+','+str(v)
                stage2v = stage2v.split(',')
                filters = generate_position_filter_end(self, k, stage2v)
                for filter in filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    endquery["$and"].append(enddictvalue)
                subqueryor["$or"].append(endquery)
                stage2v = str(int(v)+1)+','+str(9999999999)
                stage2v =stage2v.split(',')
                filters = generate_position_filter_end(self, k, stage2v)
                for filter in filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset, True)
                    length_query["$and"].append(enddictvalue)    
                length_query["$and"].append({'length': {'$gte': int(v)-int(startvalue)}}) 
            
            
        elif k == "datasets":
            pass
        elif k == "variantMinLength":
            try:
                query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                    id=VARIANTS_PROPERTY_MAP[k],
                    value='min'+v
                ), collection, dataset, True))
            except KeyError:# pragma: no cover
                raise web.HTTPNotFound
        elif k == "variantMaxLength":
            try:
                query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                    id=VARIANTS_PROPERTY_MAP[k],
                    value='max'+v
                ), collection, dataset, True))
            except KeyError:# pragma: no cover
                raise web.HTTPNotFound    
        elif k == "mateName" or k == 'referenceName':
            try:
                referencedict["$or"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                    id=VARIANTS_PROPERTY_MAP[k],
                    value=v
                ), collection, dataset, True))
            except KeyError:# pragma: no cover
                raise web.HTTPNotFound
        elif k != 'filters':
            try:
                query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                    id=VARIANTS_PROPERTY_MAP[k],
                    value=v
                ), collection, dataset, True))
            except KeyError:# pragma: no cover
                raise web.HTTPNotFound

        elif k == 'filters':
            v_list=[]
            if ',' in v:
                v_list =v.split(',')# pragma: no cover
            else:
                v_list.append(v)
            for id in v_list:
                v_dict={}
                v_dict['id']=id
                qparams.query.filters.append(v_dict)        
            return query, True
    if length_query["$and"]!=[]:
        subqueryor["$or"].append(length_query) 
    try:
        if subqueryor["$or"] != []:
            subquery["$and"].append(subqueryor)
    except Exception:# pragma: no cover
        pass
    try:
        if referencedict["$or"] != []:
            query["$and"].append(referencedict)
    except Exception:# pragma: no cover
        pass
    if subquery["$and"] != []:
        query["$and"].append(subquery)
    elif startquery["$and"] != []:
        query["$and"].append(startquery)
    return query, False