from beacon.request.parameters import AlphanumericFilter
from typing import List, Dict
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.connections.mongo.filters.alphanumeric import apply_alphanumeric_filter
from beacon.connections.mongo.__init__ import genomicVariations
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import lengthquery
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.start import generate_position_filter_start
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.sequence import generate_position_filter_start_sequence_query
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.end import generate_position_filter_end
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.mapping import VARIANTS_PROPERTY_MAP

@log_with_args(config.level)
def apply_request_parameters(self, query: Dict[str, List[dict]], dataset: str):
    # Initiate the $and operator in case is not inside the query syntax
    if len(RequestAttributes.qparams.query.requestParameters) > 0 and "$and" not in query:
        query["$and"] = []
    # Initiate the different dictionaries that will be needed to process the different request parameters use cases
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
    if 'requestProfileId' in RequestAttributes.qparams.query.requestParameters:
        if RequestAttributes.qparams.query.requestParameters['requestProfileId'] == 'BV2bracketRequest':
            start_filters = generate_position_filter_start(self, 'start', RequestAttributes.qparams.query.requestParameters['start'])
            for start_filter in start_filters:
                startdictvalue=apply_alphanumeric_filter(self, {}, start_filter, dataset, True)
                startquery["$and"].append(startdictvalue)
            end_filters = generate_position_filter_end(self, 'end', RequestAttributes.qparams.query.requestParameters['end'])
            for end_filter in end_filters:
                enddictvalue=apply_alphanumeric_filter(self, {}, end_filter, dataset, True)
                startquery["$and"].append(enddictvalue)
        elif RequestAttributes.qparams.query.requestParameters['requestProfileId'] == 'BV2rangeRequest':
            startvalue=RequestAttributes.qparams.query.requestParameters['start']
            endvalue=RequestAttributes.qparams.query.requestParameters['end']
            # Generate a final start value, as if it came by filters (start,end) to then create a list and process it as the second part of the range for the start value
            if isinstance(startvalue, list):
                finalvalue=str(startvalue[0])+','+str(endvalue[0])
            elif isinstance(endvalue, list):
                finalvalue=str(startvalue)+','+str(endvalue[0])
            else:
                finalvalue=str(startvalue)+','+str(endvalue)
            finalvalue = finalvalue.split(',')
            start_range_filters = generate_position_filter_start(self, 'start', finalvalue)
            # Build the query with those artificial filters and apply other request parameters as well, if any
            for filter in start_range_filters:
                startdict=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                startrangequery["$and"].append(startdict)  
            subqueryor["$or"].append(startrangequery)   
            # Generate a final start value, as if it came by filters (start,end) to then create a list and process it as the first part of the range for the end value
            if isinstance(endvalue, list) and isinstance(startvalue, list):
                startvalue=startvalue[0]
                v = str(endvalue[0])
                stage2v = str(startvalue)+','+v
            elif isinstance(endvalue, list):
                v = str(endvalue[0])
                stage2v = str(startvalue)+','+v
            elif isinstance(startvalue, list):
                startvalue=startvalue[0]
                stage2v = str(startvalue)+','+str(v)
            else:
                stage2v = str(startvalue)+','+str(v)
            stage2v = stage2v.split(',')
            end_range_filters = generate_position_filter_end(self, 'end', stage2v)
            # Build the query with those artificial filters and apply other request parameters as well, if any
            for filter in end_range_filters:
                enddictvalue=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                endquery["$and"].append(enddictvalue)
            subqueryor["$or"].append(endquery)
            # Generate a final end value, (end+1,9999999999) to set the second part of the range for the end value and create the filters
            stage2v = str(int(v)+1)+','+str(9999999999)
            stage2v =stage2v.split(',')
            # Get the variants that have the length greater than the range end-start
            docs_length = lengthquery(self, genomicVariations, {'length': {'$gte': int(v)-int(startvalue)}, 'datasetId': dataset})
            length_array=[]
            for lengthdoc in docs_length:
                try:
                    # Keep in an array only the records that have a start value less than the start requested and greater than the requested end
                    if int(lengthdoc["variation"]["location"]["interval"]["start"]["value"]) < int(startvalue) and int(lengthdoc["variation"]["location"]["interval"]["end"]["value"]) > int(v):
                        length_array.append(lengthdoc["_id"])
                except Exception as e:
                    continue
            # Build the length query syntax
            length_query["$and"].append({'_id': {'$in': length_array}})
        elif RequestAttributes.qparams.query.requestParameters['requestProfileId'] == 'BV2alleleRequest':
            startvalue=RequestAttributes.qparams.query.requestParameters['start']
            filters = generate_position_filter_start_sequence_query(self, 'start', startvalue)
            for filter in filters:
                query["$and"].append(apply_alphanumeric_filter(self, {}, filter, dataset, True))
    else:
        for k, v in RequestAttributes.qparams.query.requestParameters.items():
            if k == 'start' and isinstance(v, list):
                start_filters = generate_position_filter_start(self, 'start', v)
                for start_filter in start_filters:
                    startdictvalue=apply_alphanumeric_filter(self, {}, start_filter, dataset, True)
                    startquery["$and"].append(startdictvalue)
            elif k == 'start' and isinstance(v, int):
                startvalue=RequestAttributes.qparams.query.requestParameters['start']
                filters = generate_position_filter_start_sequence_query(self, 'start', v)
                for filter in filters:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, filter, dataset, True))
            elif k == 'end' and isinstance(v, list):
                end_filters = generate_position_filter_end(self, 'end', v)
                for end_filter in end_filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, end_filter, dataset, True)
                    startquery["$and"].append(enddictvalue)
            elif k == 'end' and isinstance(v, int):
                end_filters = generate_position_filter_end(self, 'end', [v])
                for end_filter in end_filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, end_filter, dataset, True)
                    startquery["$and"].append(enddictvalue)
    # Iterate through the different request parameters from the request
    for k, v in RequestAttributes.qparams.query.requestParameters.items():   
        if k == "datasets":
            pass
        elif k == "variantMinLength":
            query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                id=VARIANTS_PROPERTY_MAP[k],
                value='min'+v
            ), dataset, True))
        elif k == "variantMaxLength":
            query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                id=VARIANTS_PROPERTY_MAP[k],
                value='max'+v
            ), dataset, True))    
        elif k == "mateName" or k == 'referenceName':
            referencedict["$or"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                id=VARIANTS_PROPERTY_MAP[k],
                value=v
            ), dataset, True))
        elif k != 'filters' and k != 'assemblyId' and k != 'requestProfileId' and k != 'start' and k != 'end':
            query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                id=VARIANTS_PROPERTY_MAP[k],
                value=v
            ), dataset, True))
    if length_query["$and"]!=[] and length_query != {}:
        subqueryor["$or"].append(length_query) 
    try:
        if subqueryor["$or"] != [] and subqueryor !={}:
            subquery["$and"].append(subqueryor)
    except Exception:
        pass
    try:
        if referencedict["$or"] != [] and referencedict != {}:
            query["$and"].append(referencedict)
    except Exception:
        pass
    if subquery["$and"] != [] and subquery != {}:
        query["$and"].append(subquery)
    elif startquery["$and"] != [] and startquery != {}:
        query["$and"].append(startquery)
    return query, False