from beacon.request.parameters import AlphanumericFilter
from beacon.connections.mongo.utils import get_documents, choose_scope
from beacon.connections.mongo.__init__ import filtering_terms
from beacon.conf.filtering_terms import alphanumeric_terms
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.connections.mongo.filters.format import format_value, format_operator
from beacon.utils.modules import get_all_modules_mongo_connections_script
from beacon.connections.mongo.filters.iso8601 import iso8601_to_number
import re

@log_with_args(config.level)
def apply_alphanumeric_filter(self, query: dict, filter: AlphanumericFilter, dataset: str, isRequestParameter: bool) -> dict:
    # Format the vale and operator of the incoming alphanumeric filter
    formatted_value = format_value(self, filter.value)
    formatted_operator = format_operator(self, filter.operator)
    iso8601regex=re.compile(r"^P(?=\d)(?:\d+Y)?(?:\d+M)?(?:\d+D)?$")
    is_value_numeric=False
    try:
        iso8601regex.match(formatted_value)
        is_value_numeric=True
    except Exception:
        try:
            int(formatted_value)
            is_value_numeric=True
        except Exception:
            pass
    # If the filter is a request parameter, apply the request parameters function
    if isRequestParameter == True:
        list_modules = get_all_modules_mongo_connections_script("filters.request_parameters.alphanumeric")
        for module in list_modules:
            query = module.parse_request_parameters(self, query, filter)
    # Otherwise, apply them as regular alphanumeric filter
    elif is_value_numeric==False:
        # Check if the filter has a valid scope
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
        # Check if the filter needs to add a label in the id or not for mapping it in the database
        if filter.id in alphanumeric_terms:
            query_term = filter.id
        else:
            query_term = filter.id + '.' + 'label'
        # If the operator is =
        if formatted_operator == "$eq":
            # If is a like query, add the $regex dictionary and build the query syntax
            if '%' in filter.value:
                try: 
                    if query['$or']:
                        pass
                    else:
                        query['$or']=[]
                except Exception:
                    query['$or']=[]
                value_splitted=filter.value.split('%')
                regex_dict={}
                regex_dict['$regex']=value_splitted[1]
                query_id={}
                query_id[query_term]=regex_dict
                query['$or'].append(query_id)
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
            # Otherwise, build it as a whole text match
            else:
                try: 
                    if query['$or']:
                        pass
                    else:
                        query['$or']=[]
                except Exception:
                    query['$or']=[]
                query_id={}
                query_id[query_term]=filter.value
                query['$or'].append(query_id) 
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
                
        # If the operator is ! (not equal)
        elif formatted_operator == "$ne":
            # If is a like query, add the $regex dictionary and build the query syntax
            if '%' in filter.value:
                try: 
                    if query['$nor']:
                        pass
                    else:
                        query['$nor']=[]
                except Exception:
                    query['$nor']=[]
                value_splitted=filter.value.split('%')
                regex_dict={}
                regex_dict['$regex']=value_splitted[1]
                query_id={}
                query_id[query_term]=regex_dict
                query['$nor'].append(query_id)
            # Otherwise, build it as a whole text match
            else:
                try: 
                    if query['$nor']:
                        pass
                    else:
                        query['$nor']=[]
                except Exception:
                    query['$nor']=[]

                query_id={}
                query_id[query_term]=filter.value
                query['$nor'].append(query_id) 
    # If the value is a number
    else:
        # Check if the scope of the filtering term requested is valid
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
        # Check if is an age filter
        if "iso8601duration" in filter.id:
            # Harmonize the oeprators and the iso values
            if '>' in filter.operator:
                if 'P' in filter.value:
                    age_in_number=iso8601_to_number(self, filter)
                else:
                    try:
                        age_in_number=""
                        for char in filter.value:
                            int(char)
                            age_in_number = age_in_number+char
                    except Exception:
                        raise Exception
                new_age_list=''
                if "=" in filter.operator:
                    z = int(age_in_number)
                    while z < 150:
                        newagechar="P"+str(z)+"Y"
                        if new_age_list == '':
                            new_age_list+=newagechar
                        else:
                            new_age_list+='|'+newagechar
                        if isinstance(age_in_number, float):
                            if z == age_in_number:
                                decimal = age_in_number - round(age_in_number)
                                days=decimal*365.25
                                days=int(days)
                                months=decimal*12
                                months=int(months)
                                m = 0
                                d=0
                                while m < months:
                                    newagechar="P"+str(z)+"Y"+str(m)+"M"
                                    new_age_list+='|'+newagechar
                                    while d < days+1:
                                        newagechar="P"+str(z)+"Y"+str(m)+"M"+str(d)+"D"
                                        new_age_list+='|'+newagechar
                                        d+=1
                                    m+=1
                        z+=1
                else:
                    z = int(age_in_number)+1
                    while z < 150:
                        newagechar="P"+str(z)+"Y"
                        if new_age_list == '':
                            new_age_list+=newagechar
                        else:
                            new_age_list+='|'+newagechar
                        if isinstance(age_in_number, float):
                            if z == age_in_number:
                                decimal = age_in_number - round(age_in_number)
                                days=decimal*365.25
                                days=int(days)
                                months=decimal*12
                                months=int(months)
                                m = 0
                                d=0
                                while m < months:
                                    newagechar="P"+str(z)+"Y"+str(m)+"M"
                                    new_age_list+='|'+newagechar
                                    while d < days:
                                        newagechar="P"+str(z)+"Y"+str(m)+"M"+str(d)+"D"
                                        new_age_list+='|'+newagechar
                                        d+=1
                                    m+=1
                        z+=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
            elif '<' in filter.operator:
                if 'P' in filter.value:
                    age_in_number=iso8601_to_number(self, filter)
                else:
                    try:
                        age_in_number=""
                        for char in filter.value:
                            int(char)
                            age_in_number = age_in_number+char
                    except Exception:
                        raise Exception
                new_age_list=''
                if "=" in filter.operator:
                    z = int(age_in_number)
                    while z >0:
                        newagechar="P"+str(z)+"Y"
                        if new_age_list == '':
                            new_age_list+=newagechar
                        else:
                            new_age_list+='|'+newagechar
                        if isinstance(age_in_number, float):
                            if z == age_in_number:
                                decimal = age_in_number - round(age_in_number)
                                days=decimal*365.25
                                days=int(days)
                                months=decimal*12
                                months=int(months)
                                m = 0
                                d=0
                                while months>0:
                                    newagechar="P"+str(z)+"Y"+str(months)+"M"
                                    new_age_list+='|'+newagechar
                                    while days>0:
                                        newagechar="P"+str(z)+"Y"+str(months)+"M"+str(days)+"D"
                                        new_age_list+='|'+newagechar
                                        d+=1
                                    months-=1
                        z-=1
                else:
                    z = int(age_in_number)-1
                    while z >0:
                        newagechar="P"+str(z)+"Y"
                        if new_age_list == '':
                            new_age_list+=newagechar
                        else:
                            new_age_list+='|'+newagechar
                        if isinstance(age_in_number, float):
                            if z == age_in_number:
                                decimal = age_in_number - round(age_in_number)
                                days=decimal*365.25
                                days=int(days)-1
                                months=decimal*12
                                months=int(months)
                                while months>0:
                                    newagechar="P"+str(z)+"Y"+str(months)+"M"
                                    new_age_list+='|'+newagechar
                                    while days>0:
                                        newagechar="P"+str(z)+"Y"+str(months)+"M"+str(days)+"D"
                                        new_age_list+='|'+newagechar
                                        days-=1
                                    months-=1
                        z-=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
            elif '=' in filter.operator:
                if 'P' in filter.value:
                    age_in_number=iso8601_to_number(self, filter)
                else:
                    age_in_number=""
                    for char in filter.value:
                        try:
                            int(char)
                            age_in_number = age_in_number+char
                        except Exception:
                            continue
                z = int(age_in_number)
                if isinstance(age_in_number, float):
                    decimal = age_in_number - round(age_in_number)
                    days=decimal*365.25
                    days=int(days)
                    months=decimal*12
                    months=int(months)
                    newagechar="P"+str(z)+"Y"+str(months)+"M"+str(days)+"D"
                    new_age_list="P"+str(z)+"Y"+str(months)+"M"+str(days)+"D"+"|"+"P"+str(z)+"Y"+str(months)+"M"+"|"+"P"+str(z)+"Y"
                else:
                    new_age_list="P"+str(z)+"Y"
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
        elif '.' in filter.id:
            splitfilterid= filter.id.split('.')
            keyfilterid = ".".join(splitfilterid[1:])
            dict_in={}
            dict_in["$elemMatch"]= {
                keyfilterid: { formatted_operator: formatted_value }
                }
            query[splitfilterid[0]]=dict_in
            list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
            for module in list_modules:
                query = module.cross_query(self, query, scope, {}, dataset)
        # If it's not an age filter, is a measurement filter
        else:
            # Find the filter in filtering terms
            query_filtering={}
            query_filtering['$and']=[]
            dict_type={}
            dict_id={}
            dict_regex={}
            dict_regex['$regex']=filter.id
            dict_regex['$options']='i'
            dict_type['type']='custom'
            dict_id['id']=dict_regex
            query_filtering['$and'].append(dict_type)
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
            # Check if it's measures or measurements
            for doc in docs:
                prefield_splitted = doc['id'].split(':')
                prefield = prefield_splitted[0]
            field = prefield.replace('assayCode', 'measurementValue.value')
            
            assayfield = 'assayCode' + '.label'
            fieldsplitted = field.split('.')
            measuresfield=fieldsplitted[0]

            field = field.replace(measuresfield+'.', '')
            # Build the final query syntax
            query[field] = { formatted_operator: float(formatted_value) }
            query[assayfield]=filter.id
            dict_elemmatch={}
            dict_elemmatch['$elemMatch']=query
            dict_measures={}
            dict_measures[measuresfield]=dict_elemmatch
            query = dict_measures
            list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
            for module in list_modules:
                query = module.cross_query(self, query, scope, {}, dataset)
    return query