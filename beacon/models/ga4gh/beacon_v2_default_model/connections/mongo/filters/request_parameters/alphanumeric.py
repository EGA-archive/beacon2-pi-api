from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.mongo.filters.format import format_value, format_operator
from beacon.request.classes import RequestAttributes

@log_with_args(level)
def parse_request_parameters(self, query, filter):
    # Processing the request parameters as filters, checking which is the id of the property mapped by the request parameter (where the requestParameter points at, several can apply to one property)
    if filter.id == "identifiers.genomicHGVSId":
        # Initialize a dictionary to use for the chromosome query and create the list of chromosome values accepted that come from requestParameters
        list_chromosomes = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','X','Y','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chr24','chrX','chrY']
        dict_regex={}
        # Check if the value of the chromosome is accepted
        if filter.value in list_chromosomes:
            # If is a mitochondrial, build the root of the HGVSId as specified
            if filter.value == 'MT':
                dict_regex['$regex']='NC_012920.1:m'
            # If is not mitochondrial, taking the ref genome and the value of the chromosome, build the root of the HGVSId
            else:
                if 'chr' in filter.value:
                    filter.value=filter.value.replace('chr', '')
                if len(filter.value) == 2:
                    prehgvs='^NC_0000'
                elif len(filter.value) == 1:
                    prehgvs='^NC_00000'
                if filter.value == 'X':
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']='^NC_000023'+filter.value+'.'+'9:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']='^NC_000023'+filter.value+'.'+'10:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']='^NC_000023'+filter.value+'.'+'11:g'
                elif filter.value == 'Y':
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']='^NC_000024'+filter.value+'.'+'8:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']='^NC_000024'+filter.value+'.'+'9:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']='^NC_000024'+filter.value+'.'+'10:g'
                elif filter.value in ['14', '21']:
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'7:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'8:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'9:g'
                elif filter.value in ['5', '11', '15', '16', '18', '19', '24']:
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'8:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'9:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'10:g'
                elif filter.value in ['1', '8', '10', '13', '17', '20', '22', '23']:
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'9:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'10:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'11:g'
                elif filter.value in ['2', '3', '4', '6', '9', '12']:
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'10:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'11:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'12:g'
                elif filter.value == '7':
                    if RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'NCBI36':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'12:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh37':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'13:g'
                    elif RequestAttributes.qparams.query.requestParameters["assemblyId"] == 'GRCh38':
                        dict_regex['$regex']=prehgvs+filter.value+'.'+'14:g'
        # If there is &gt; in the value, replace it by >
        elif '&gt;' in filter.value:
            newvalue=filter.value.replace("&gt;",">")
            dict_regex=newvalue
        # If there is a dot in the value, execute a "si" query, to ignore end of the value 
        elif '.' in filter.value:
            dict_regex['$regex']=filter.value
            dict_regex['$options']= "si"
        query[filter.id] = dict_regex
    elif filter.id == 'molecularAttributes.aminoacidChanges':
        query[filter.id] = filter.value
    elif filter.id == 'molecularAttributes.geneIds':
        query[filter.id] = filter.value
    elif filter.id == "caseLevelData.clinicalInterpretations.clinicalRelevance":
        query[filter.id] = filter.value
    elif filter.id == "variation.alternateBases":
        # If a max is sent in the value of the request parameter, count the number of bases of the variant to limit the max length value. The strLenCP counts length of bases in a string in mongoDB.
        if 'max' in filter.value:
            valuereplaced = filter.value.replace('max', '')
            length=int(valuereplaced)+2
            array_min=[]
            dict_len={}
            dict_len['$strLenCP']="$variation.alternateBases"
            array_min.append(dict_len)
            array_min.append(length)
            dict_gt={}
            dict_gt['$lt']=array_min
            dict_expr={}
            dict_expr['$expr']=dict_gt
            andquery={}
            andquery["$and"]=[]
            andquery["$and"].append(dict_expr)
            array_min=[]
            dict_len={}
            dict_len['$strLenCP']="$variation.referenceBases"
            array_min.append(dict_len)
            array_min.append(length)
            dict_gt={}
            dict_gt['$lt']=array_min
            dict_expr={}
            dict_expr['$expr']=dict_gt
            andquery["$and"].append(dict_expr)
            query=andquery


        elif 'min' in filter.value:
            # If a min is sent in the value of the request parameter, count the number of bases of the variant to limit the min length value. The strLenCP counts length of bases in a string in mongoDB.
            valuereplaced = filter.value.replace('min', '')
            length=int(valuereplaced)
            array_min=[]
            dict_len={}
            dict_len['$strLenCP']="$variation.alternateBases"
            array_min.append(dict_len)
            array_min.append(length)
            dict_gt={}
            dict_gt['$gt']=array_min
            dict_expr={}
            dict_expr['$expr']=dict_gt
            andquery={}
            andquery["$and"]=[]
            andquery["$and"].append(dict_expr)
            array_min=[]
            dict_len={}
            dict_len['$strLenCP']="$variation.referenceBases"
            array_min.append(dict_len)
            array_min.append(length)
            dict_gt={}
            dict_gt['$gt']=array_min
            dict_expr={}
            dict_expr['$expr']=dict_gt
            andquery["$and"].append(dict_expr)
            query=andquery

    elif filter.id == 'assemblyId':
        pass





    else:
        formatted_value = format_value(self, filter.value)
        formatted_operator = format_operator(self, filter.operator)
        query[filter.id] = { formatted_operator: formatted_value }
    return query