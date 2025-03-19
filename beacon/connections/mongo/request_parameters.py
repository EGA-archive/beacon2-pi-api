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
    if len(qparams.query.request_parameters) > 0 and "$and" not in query:
        query["$and"] = []
    if isinstance(qparams.query.request_parameters, list):# pragma: no cover
        query={}
        query["$or"]=[]
        for reqparam in qparams.query.request_parameters:
            subquery={}
            subquery["$and"] = []
            startquery={}
            endquery={}
            startendquery={}
            startendquery["$and"] = []
            subqueryor={}
            subqueryor["$or"] = []
            equal=True
            endvalue=0
            isBracket=False
            for k, v in reqparam.items():
                if k == 'end':
                    equal=False
                    endvalue=v
            for k, v in reqparam.items():
                if k == "start":
                    if isinstance(v, str):
                        v = v.split(',')
                        isBracket==True
                    if equal == True:
                        filters = generate_position_filter_start_sequence_query(self, k, v)
                    else:
                        filters = generate_position_filter_start(self, k, v)
                    for filter in filters:
                        if filter.id == "start":
                            filter[id]=VARIANTS_PROPERTY_MAP["start"]
                            startquery=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                elif k == "end":
                    if isinstance(v, str):
                        v = v.split(',')
                    filters = generate_position_filter_end(self, k, v)
                    for filter in filters:
                        if filter.id == "end":
                            filter[id]=VARIANTS_PROPERTY_MAP["end"]
                            endquery=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                elif k == "datasets":
                    pass
                elif k == "variantMinLength":
                    try:
                        subquery["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                            id=VARIANTS_PROPERTY_MAP[k],
                            value='min'+v
                        ), collection, dataset))
                    except KeyError:
                        raise web.HTTPNotFound
                elif k == "variantMaxLength":
                    try:
                        subquery["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                            id=VARIANTS_PROPERTY_MAP[k],
                            value='max'+v
                        ), collection, dataset))
                    except KeyError:
                        raise web.HTTPNotFound    
                elif k == "mateName" or k == 'referenceName':
                    try:
                        subqueryor["$or"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                            id=VARIANTS_PROPERTY_MAP[k],
                            value='max'+v
                        ), collection, dataset))
                    except KeyError:
                        raise web.HTTPNotFound    
                elif k != 'filters':
                    try:
                        subquery["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                            id=VARIANTS_PROPERTY_MAP[k],
                            value=v
                        ), collection, dataset))
                    except KeyError:
                        raise web.HTTPNotFound

                elif k == 'filters':
                    v_list=[]
                    if ',' in v:
                        v_list =v.split(',')
                    else:
                        v_list.append(v)
                    for id in v_list:
                        v_dict={}
                        v_dict['id']=id
                        qparams.query.filters.append(v_dict)        
                    return query, True
        try:
            if subqueryor["$or"] != []:
                subquery["$and"].append(subqueryor)
            if startquery["$and"] != []:
                subquery["$or"].append(startquery)
            if endquery["$and"] != []:
                subquery["$or"].append(endquery)
            if startendquery["$and"] != []:
                subquery["$or"].append(startendquery)
        except Exception:
            pass
        query["$or"].append(subquery)
    else:
        subquery={}
        subquery["$and"] = []
        subqueryor={}
        subqueryor["$or"] = []
        startquery={}
        startquery["$and"]=[]
        endquery={}
        endquery["$and"]=[]
        definitive_variantIds=[]
        equal=False
        isBracket=False
        for k, v in qparams.query.request_parameters.items():
            if k == 'end':
                equal=True
                endvalue=v
        for k, v in qparams.query.request_parameters.items():
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
                        query["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                elif isBracket == True:
                    filters = generate_position_filter_start(self, k, v)
                    for filter in filters:
                        startdictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                        startquery["$and"].append(startdictvalue)
                else:
                    startvalue=v
                    if isinstance(endvalue, list):
                        finalvalue=str(0)+','+str(endvalue[0])
                    else:
                        finalvalue=str(0)+','+str(endvalue)
                    finalvalue = finalvalue.split(',')
                    filters = generate_position_filter_start(self, k, finalvalue)
                    for filter in filters:
                        startdictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                        startquery["$and"].append(startdictvalue)            
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
                        enddictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                        startquery["$and"].append(enddictvalue)
                    query["$and"].append(startquery)    
                elif isBracket==False:
                    v = str(startvalue[0])+','+str(9999999999)
                    v = v.split(',')
                    filters = generate_position_filter_end(self, k, v)
                    for filter in filters:
                        enddictvalue=apply_alphanumeric_filter(self, {}, filter, collection, dataset)
                        startquery["$and"].append(enddictvalue)
                    query["$and"].append(startquery)    
                
                
            elif k == "datasets":
                pass
            elif k == "variantMinLength":
                try:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                        id=VARIANTS_PROPERTY_MAP[k],
                        value='min'+v
                    ), collection, dataset))
                except KeyError:# pragma: no cover
                    raise web.HTTPNotFound
            elif k == "variantMaxLength":
                try:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                        id=VARIANTS_PROPERTY_MAP[k],
                        value='max'+v
                    ), collection, dataset))
                except KeyError:# pragma: no cover
                    raise web.HTTPNotFound    
            elif k == "mateName" or k == 'referenceName':
                try:
                    subqueryor["$or"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                        id=VARIANTS_PROPERTY_MAP[k],
                        value=v
                    ), collection, dataset))
                except KeyError:# pragma: no cover
                    raise web.HTTPNotFound
            elif k != 'filters':
                try:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                        id=VARIANTS_PROPERTY_MAP[k],
                        value=v
                    ), collection, dataset))
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
        try:
            if subqueryor["$or"] != []:
                subquery["$and"].append(subqueryor)
        except Exception:# pragma: no cover
            pass
        if subquery["$and"] != []:
            query["$and"].append(subquery)
        elif startquery["$and"] != []:
            query["$and"].append(startquery)
    return query, False