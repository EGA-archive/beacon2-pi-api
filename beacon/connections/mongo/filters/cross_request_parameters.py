 
def cross_request_parameters(self, total_query): 
    if RequestAttributes.entry_type == individual.endpoint_name:
        biosampleIds=get_biosampleIds(self, request_parameters, query, dataset)
        try:
            finalquery={}
            finalquery["$or"]=[]
            for finalid in biosampleIds:
                query = {"id": finalid}
                finalquery["$or"].append(query)
            individual_id = biosamples \
                .find(finalquery, {"individualId": 1, "_id": 0})
            try:
                finalids=[]
                for indid in individual_id:
                    finalids.append(indid["individualId"])
            except Exception:
                finalids=[]
            if finalids==[]:
                finalids=biosampleIds
        except Exception:
            finalids=biosampleIds
        finalquery={}
        finalquery["$or"]=[]
        for finalid in finalids:
            query = {"id": finalid}
            finalquery["$or"].append(query)
        try:
            total_query["$and"].append(finalquery)
        except Exception:
            total_query["$and"]=[]
            total_query["$and"].append(finalquery)
    elif RequestAttributes.entry_type == biosample.endpoint_name:
        biosampleIds=get_biosampleIds(self, request_parameters, query, dataset)
        total_query=get_total_query(self, biosampleIds, total_query, "id")
    elif RequestAttributes.entry_type == analysis.endpoint_name or RequestAttributes.entry_type == run.endpoint_name:
        biosampleIds=get_biosampleIds(self, request_parameters, query, dataset)
        total_query=get_total_query(self, biosampleIds, total_query, "biosampleId")
    else:
        try:
            total_query["$and"].append(request_parameters)
        except Exception:
            total_query["$and"]=[]
            total_query["$and"].append(request_parameters)
    return total_query