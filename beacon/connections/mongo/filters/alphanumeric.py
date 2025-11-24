from beacon.request.parameters import AlphanumericFilter
from beacon.connections.mongo.utils import get_documents, choose_scope
from beacon.connections.mongo.__init__ import filtering_terms
from beacon.conf.filtering_terms import alphanumeric_terms
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.mongo.filters.format import format_value, format_operator
from beacon.utils.modules import get_all_modules_mongo_connections_script

@log_with_args(level)
def apply_alphanumeric_filter(self, query: dict, filter: AlphanumericFilter, dataset: str, isRequestParameter: bool) -> dict:
    formatted_value = format_value(self, filter.value)
    formatted_operator = format_operator(self, filter.operator)
    if isRequestParameter == True:
        list_modules = get_all_modules_mongo_connections_script("filters.request_parameters.alphanumeric")
        for module in list_modules:
            query = module.parse_request_parameters(self, query, filter)
    elif isinstance(formatted_value,str):
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
        if filter.id in alphanumeric_terms:
            query_term = filter.id
        else:
            query_term = filter.id + '.' + 'label'
        if formatted_operator == "$eq":
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
                

        elif formatted_operator == "$ne":
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
        
    else:
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
        if "iso8601duration" in filter.id:
            if '>' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:
                        continue
                new_age_list=''
                
                if "=" in filter.operator:
                    z = int(age_in_number)
                else:
                    z = int(age_in_number)+1
                while z < 150:
                    newagechar="P"+str(z)+"Y"
                    if new_age_list == '':
                        new_age_list+=newagechar
                    else:
                        new_age_list+='|'+newagechar
                    z+=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
            elif '<' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:
                        continue
                new_age_list=''
                if "=" in filter.operator:
                    z = int(age_in_number)
                else:
                    z = int(age_in_number)-1
                while z > 0:
                    newagechar="P"+str(z)+"Y"
                    if new_age_list == '':
                        new_age_list+=newagechar
                    else:
                        new_age_list+='|'+newagechar
                    z-=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
            elif '=' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:
                        continue
                z = int(age_in_number)
                newagechar="P"+str(z)+"Y"
                dict_in={}
                dict_in["$regex"]=newagechar
                query[filter.id] = dict_in
                list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
                for module in list_modules:
                    query = module.cross_query(self, query, scope, {}, dataset)
        else:
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
            for doc in docs:
                prefield_splitted = doc['id'].split(':')
                prefield = prefield_splitted[0]
            field = prefield.replace('assayCode', 'measurementValue.value')
            
            assayfield = 'assayCode' + '.label'
            fieldsplitted = field.split('.')
            measuresfield=fieldsplitted[0]

            field = field.replace(measuresfield+'.', '')

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