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
    # Check for the existance of end/start parameters to create some values that will help later to process each one of those parameters individually
    for k, v in RequestAttributes.qparams.query.requestParameters.items():
        if k == 'end':
            equal=True
            endvalue=v
        if k == 'start':
            startvalue=v
    # Iterate through the different request parameters from the request
    for k, v in RequestAttributes.qparams.query.requestParameters.items():
        if k == "start":
            # First, get how many parameters are being thrown and if there is more than one, assign the query to a bracket query.
            if isinstance(v, str):
                v = v.split(',')
                if len(v)>1:
                    isBracket=True
            elif isinstance(v, list) and len(v) > 1:
                isBracket=True
            # If there is no end, process the parameter as a sequence query
            if equal == False:
                filters = generate_position_filter_start_sequence_query(self, k, v)
                for filter in filters:
                    query["$and"].append(apply_alphanumeric_filter(self, {}, filter, dataset, True))
            # If there is end and query is bracket, process the parameter as a bracket query
            elif isBracket == True:
                filters = generate_position_filter_start(self, k, v)
                for filter in filters:
                    startdictvalue=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                    startquery["$and"].append(startdictvalue)
            # Otherwise, process the query as a range query
            else:
                startvalue=v
                # Generate a final start value, as if it came by filters (0,start-1) to then create a list and process it as the first part of the range for the start value
                if isinstance(startvalue, list):
                    finalvalue=str(0)+','+str(startvalue[0]-1)
                else:
                    finalvalue=str(0)+','+str(startvalue-1)
                finalvalue = finalvalue.split(',')
                filters = generate_position_filter_start(self, k, finalvalue)
                # Generate a final start value, as if it came by filters (start,end) to then create a list and process it as the second part of the range for the start value
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
                # Build the query with those artificial filters and apply other request parameters as well, if any
                for filter in filters:
                    startdict=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                    startrangequery["$and"].append(startdict)  
                subqueryor["$or"].append(startrangequery)            
        elif k == "end":
            # First, get how many parameters are being thrown and if there is more than one, assign the query to a bracket query.
            if isinstance(v, str):
                v = v.split(',')
                if len(v)>1:
                    isBracket=True
            elif isinstance(v, list) and len(v) > 1:
                isBracket=True
            filters = generate_position_filter_end(self, k, v)
            # If there is start and query is bracket, process the parameter as a bracket query
            if isBracket==True:
                for filter in filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                    startquery["$and"].append(enddictvalue)
                query["$and"].append(startquery)    
            # Otherwise, process the parameter as a range query
            elif isBracket==False:
                # Generate a final start value, as if it came by filters (start,end) to then create a list and process it as the first part of the range for the end value
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
                # Build the query with those artificial filters and apply other request parameters as well, if any
                for filter in filters:
                    enddictvalue=apply_alphanumeric_filter(self, {}, filter, dataset, True)
                    endquery["$and"].append(enddictvalue)
                subqueryor["$or"].append(endquery)
                # Generate a final end value, (end+1,9999999999) to set the second part of the range for the end value and create the filters
                stage2v = str(int(v)+1)+','+str(9999999999)
                stage2v =stage2v.split(',')
                filters = generate_position_filter_end(self, k, stage2v)  
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
        elif k == "datasets":
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
        elif k != 'filters' and k != 'assemblyId':
            query["$and"].append(apply_alphanumeric_filter(self, {}, AlphanumericFilter(
                id=VARIANTS_PROPERTY_MAP[k],
                value=v
            ), dataset, True))
    if length_query["$and"]!=[]:
        subqueryor["$or"].append(length_query) 
    try:
        if subqueryor["$or"] != []:
            subquery["$and"].append(subqueryor)
    except Exception:
        pass
    try:
        if referencedict["$or"] != []:
            query["$and"].append(referencedict)
    except Exception:
        pass
    if subquery["$and"] != []:
        query["$and"].append(subquery)
    elif startquery["$and"] != []:
        query["$and"].append(startquery)
    return query, False