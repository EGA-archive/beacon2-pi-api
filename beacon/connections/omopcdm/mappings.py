
# File for all the mappings from the Beacon v2 specification and the results of the SQL Queries

## Individual model ##

def diseases_table_map(dictValues):
    return {
            'diseaseCode': dictValues["condition_concept_id"],
            'ageOfOnset': {'iso8601duration': dictValues["condition_ageOfOnset"]},
        }

def procedures_table_map(dictValues):
    return {
            'procedureCode': dictValues["procedure_concept_id"],
            'ageAtProcedure': {'iso8601duration': dictValues["procedure_ageOfOnset"]},
            'dateOfProcedure': dictValues["procedure_date"],
        }

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def convertToNum(num):
    try:
        float(num)
        return float(num)
    except ValueError:
        pass

    


def measures_table_map(dictValues):
    # TO DO
    # Make the return complex so depend on the type of data. It can be a unit/value, an ontology, referenceRange, complexValue, etc.
    
    measures_dict ={
        'assayCode': dictValues["measurement_concept_id"],
        'date' : dictValues["measurement_date"],
        'observationMoment': {'iso8601duration':dictValues["measurement_ageOfOnset"]}
    }
    if  dictValues["value_source_value"] is None: # Return null Ontology term
        measure_value_dict = {'measurementValue': dictValues["unit_concept_id"]}
    else:
        if isfloat(str(dictValues["value_source_value"])): # If numeric value
            measure_value_dict = {
                'measurementValue': {
                    'unit': dictValues["unit_concept_id"],
                    'value': convertToNum(dictValues["value_source_value"])
                }
            }
        else:
            measure_value_dict = {'measurementValue': {
                'id': 'None:None',
                'label': dictValues["value_source_value"]
            }}

    return {**measures_dict, **measure_value_dict}

def exposures_table_map(dictValues):
    return {
            'exposureCode': dictValues["observation_concept_id"],
            'ageAtExposure': {'iso8601duration': dictValues["observation_ageOfOnset"]},
            'date': dictValues["observation_date"],
            'unit': dictValues["unit_concept_id"],
            'duration':dictValues["duration"]
        }

def treatments_table_map(dictValues):
    return {
            'treatmentCode': dictValues["drugExposure_concept_id"],
            'ageOfOnset': {'iso8601duration': dictValues["drugExposure_ageOfOnset"]},
        }