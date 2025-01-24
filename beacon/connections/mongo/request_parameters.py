from beacon.request.parameters import RequestParams, AlphanumericFilter, Operator
from typing import List, Dict
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from aiohttp import web
from beacon.connections.mongo.filters import apply_alphanumeric_filter

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

def generate_position_filter_start_2(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP["end"],
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

def generate_position_filter_start_3(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.LESS_EQUAL
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
def generate_position_filter_end_2(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP["start"],
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
def generate_position_filter_end_3(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
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
            startquery["$and"] = []
            endquery={}
            endquery["$and"] = []
            startendquery={}
            startendquery["$and"] = []
            subqueryor={}
            subqueryor["$or"] = []
            equal=True
            for k, v in reqparam.items():
                if k == 'end':
                    equal=False
            for k, v in reqparam.items():
                if k == "start":
                    if isinstance(v, str):
                        v = v.split(',')
                    if equal == True:
                        filters = generate_position_filter_start_sequence_query(self, k, v)
                    else:
                        filters = generate_position_filter_start(self, k, v)
                    for filter in filters:
                        if filter.id == "start":
                            filter[id]=VARIANTS_PROPERTY_MAP["start"]
                            startquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                        elif filter.id == "start2":
                            filter[id]=VARIANTS_PROPERTY_MAP["start"]
                            startquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                        elif filter.id == "start3":
                            filter[id]=VARIANTS_PROPERTY_MAP["start"]
                            startendquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                elif k == "end":
                    if isinstance(v, str):
                        v = v.split(',')
                    filters = generate_position_filter_end(self, k, v)
                    for filter in filters:
                        if filter.id == "end":
                            filter[id]=VARIANTS_PROPERTY_MAP["end"]
                            endquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                        elif filter.id == "end2":
                            filter[id]=VARIANTS_PROPERTY_MAP["end"]
                            endquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                        elif filter.id == "end3":
                            filter[id]=VARIANTS_PROPERTY_MAP["end"]
                            startendquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
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
        startquery["$and"] = []
        endquery={}
        endquery["$and"] = []
        startendquery={}
        startendquery["$and"] = []
        equal=False
        for k, v in qparams.query.request_parameters.items():
            if k == 'end':
                equal=True
        for k, v in qparams.query.request_parameters.items():
            if k == "start":
                if isinstance(v, str):
                    v = v.split(',')
                if equal == False:
                    filters = generate_position_filter_start_sequence_query(self, k, v)
                    for filter in filters:
                        query["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                else:
                    filters = generate_position_filter_start(self, k, v)
                    filters2=generate_position_filter_start_2(self, k, v)
                    filters3=generate_position_filter_start_3(self, k, v)
                    for filter in filters:
                        startquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                    for filter in filters2:
                        endquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                    for filter in filters3:
                        startendquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
            elif k == "end":
                if isinstance(v, str):
                    v = v.split(',')
                filters = generate_position_filter_end(self, k, v)
                filters2 = generate_position_filter_end_2(self, k, v)
                filters3 = generate_position_filter_end_3(self, k, v)
                for filter in filters:
                    endquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                for filter in filters2:
                    startquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
                for filter in filters3:
                    startendquery["$and"].append(apply_alphanumeric_filter(self, {}, filter, collection, dataset))
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
        if startquery["$and"] != []:
            try:
                query["$or"].append(startquery)
            except Exception:
                query["$or"]=[]
                query["$or"].append(startquery)
        if endquery["$and"] != []:
            try:
                query["$or"].append(endquery)
            except Exception:# pragma: no cover
                query["$or"]=[]
                query["$or"].append(endquery)
        if startendquery["$and"] != []:
            try:
                query["$or"].append(startendquery)
            except Exception:# pragma: no cover
                query["$or"]=[]
                query["$or"].append(startendquery)


    return query, False