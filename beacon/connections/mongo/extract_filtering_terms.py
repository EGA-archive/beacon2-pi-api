import os.path
from typing import List, Dict
import re
import progressbar
from bson.objectid import ObjectId
from tqdm import tqdm
from bson.json_util import dumps
import json
import os
from beacon.connections.mongo.__init__ import dbname, filtering_terms as filtering_terms_, client
from beacon.conf.filtering_terms import alphanumeric_terms_individuals, alphanumeric_terms_g_variants, alphanumeric_terms_analyses, alphanumeric_terms_biosamples, alphanumeric_terms_cohorts, alphanumeric_terms_datasets, alphanumeric_terms_runs, alphanumeric_terms_patients
from beacon.utils.modules import get_modules_confiles
from beacon.connections.mongo.__init__ import biosamples, cohorts, datasets, genomicVariations, imagestudies, individuals, patients, runs

ONTOLOGY_REGEX = re.compile(r"([_A-Za-z0-9]+):([_A-Za-z0-9^\-]+)")
ICD_REGEX = re.compile(r"(ICD[_A-Za-z0-9]+):([_A-Za-z0-9^\./-]+)")

class MyProgressBar:
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num: int, block_size: int, total_size: int):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def get_ontology_field_name(ontology_id:str, term_id:str, collection:str, fields):

    # Save the properties in a common array variable
    # Generate the query syntax for the ontology search for all the requested fields/properties
    query={}
    query['$or']=[]
    for field in fields:
        fieldquery={}
        fieldquery[field]=ontology_id + ":" + term_id
        query['$or'].append(fieldquery)
    # Execute the query
    results = client[dbname].get_collection(collection).find(query).limit(1)
    # Get the results in a dictionary and extract the labels of the ontologies
    try:
        results = list(results)
        results = dumps(results)
        results = json.loads(results)
    except Exception:
        results=[]
    if results != []:
        field = ''
        for result in results:
            for k, v in result.items():
                if isinstance(v, str): 
                    if v == ontology_id + ':' + term_id:
                        field = k
                        for key, value in result.items():
                            if key == 'label':
                                label = value
                            break
                        break
                elif isinstance(v, dict):
                    for k2, v2 in v.items():
                        if isinstance(v2, list):
                            for item_list in v2:
                                if isinstance(item_list, str): 
                                    if item_list == ontology_id + ':' + term_id:
                                        field = k + '.' + k2
                                        for key, value in v.items():
                                            if key == 'label':
                                                label = value
                                                break
                                        break
                                elif isinstance(item_list, dict):
                                    for k21, v21 in item_list.items():
                                        if isinstance(v21, str):
                                            if v21 == ontology_id + ':' + term_id:
                                                field = k + '.' + k2 + '.' + k21
                                                for key, value in item_list.items():
                                                    if key == 'label':
                                                        label = value
                                                        break
                                                break
                                        elif isinstance(v21,dict):
                                            for k22, v22 in v21.items():
                                                if v22 == v21 == ontology_id + ':' + term_id:
                                                    field = k + '.' + k2 + '.' + k22
                                                    for key, value in v21.items():
                                                        if key == 'label':
                                                            label = value
                                                            break
                                                    break
                        elif v2 == ontology_id + ':' + term_id:
                            field = k + '.' + k2
                            for key, value in v.items():
                                if key == 'label':
                                    label = value
                                    break
                            break
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str): 
                            if item == ontology_id + ':' + term_id:
                                field = k
                                for key, value in result.items():
                                    if key == 'label':
                                        label = value
                                        break
                                break
                        elif isinstance(item, dict):
                            for k2, v2 in item.items():
                                if isinstance(v2, str):
                                    if v2 == ontology_id + ':' + term_id:
                                        field = k + '.' + k2
                                        for key, value in item.items():
                                            if key == 'label':
                                                label = value
                                                break
                                        break
                                elif isinstance(v2, dict):
                                    for k3, v3 in v2.items():
                                        if isinstance(v3, str):
                                            if v3 == ontology_id + ':' + term_id:
                                                field = k + '.' + k2 + '.' + k3
                                                for key, value in v2.items():
                                                    if key == 'label':
                                                        label = value
                                                        break
                                                break 
                                        elif isinstance(v3, dict):
                                            for k4, v4 in v3.items():
                                                if isinstance(v4, str):
                                                    if v4 == ontology_id + ':' + term_id:
                                                        field = k + '.' + k2 + '.' + k3 + '.' + k4
                                                        for key, value in v3.items():
                                                            if key == 'label':
                                                                label = value
                                                                break
                                                        break 
                                                elif isinstance(v4, dict):
                                                    for k5, v5 in v4.items():
                                                        if v5 == ontology_id + ':' + term_id:
                                                            field = k + '.' + k2 + '.' + k3 + '.' + k4 + '.' + k5
                                                            for key, value in v4.items():
                                                                if key == 'label':
                                                                    label = value
                                                                    break
                                                            break 

        # Return a dictionary with the field and the label obtained
        if '.' in field:
            try:
                final_field = ''
                field_split = field.split('.')
                del field_split[-1]
                for item in field_split:
                    if final_field == '':
                        final_field = item
                    else:
                        final_field = final_field + '.' + item
                final_dict={}
                final_dict['field']=final_field
                final_dict['label']=label
                return final_dict
            except Exception:
                pass
        else:
            pass

def insert_found_terms(collection, fields_names):
    if collection.name not in ['counts', 'similarities', 'synonyms', 'caseLevelData', 'targets', 'budget']:
        terms_ids = find_ontology_terms_used(collection)
        terms = get_filtering_object(terms_ids, collection, fields_names)
        if len(terms) > 0:
            filtering_terms_.insert_many(terms)


def insert_all_ontology_terms_used():
    #Get all the yml conf files for each entity
    list_of_modules=get_modules_confiles()
    #Map the files and if they are enabled, give the relationship of fields that host ontologies
    alphanumterms=[]
    for module in list_of_modules:
        for entity, params in module.items():
            if params['entry_type_enabled']==True:
                if entity == 'analysis':
                    for alphanumeric_term in alphanumeric_terms_analyses:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['analysis']
                                            })
                if entity == 'biosample':
                    biosamples_fields=['biosampleStatus.id','diagnosticMarkers.id','histologicalDiagnosis.id','measurements.assayCode.id','measurements.measurementValue.id','measurements.measurementValue.referenceRange.unit.id','measurements.measurementValue.typedQuantities.quantity.unit.id','measurements.measurementValue.unit.id','measurements.observationMoment.id','measurements.procedure.bodySite.id','measurements.procedure.procedureCode.id','pathologicalStage.id','pathologicalTnmFinding.id','phenotypicFeatures.evidence.evidenceCode.id','phenotypicFeatures.evidence.reference.id','phenotypicFeatures.featureType.id','phenotypicFeatures.modifiers.id','phenotypicFeatures.onset.id','phenotypicFeatures.resolution.id','phenotypicFeatures.severity.id','sampleOriginDetail.id','sampleOriginType.id','sampleProcessing.id','sampleStorage.id','tumorGrade.id','tumorProgression.id']
                    insert_found_terms(biosamples, biosamples_fields)
                    for alphanumeric_term in alphanumeric_terms_biosamples:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['biosample']
                                            })
                elif entity == 'cohort':
                    cohorts_fields=['cohortDataTypes.id','cohortDesign.id','exclusionCriteria.diseaseConditions.diseaseCode.id','exclusionCriteria.diseaseConditions.severity.id','exclusionCriteria.diseaseConditions.stage.id','exclusionCriteria.ethnicities.id','exclusionCriteria.genders.id','exclusionCriteria.locations.id','exclusionCriteria.phenotypicConditions.featureType.id','exclusionCriteria.phenotypicConditions.severity.id','inclusionCriteria.diseaseConditions.diseaseCode.id','inclusionCriteria.diseaseConditions.severity.id','inclusionCriteria.diseaseConditions.stage.id','inclusionCriteria.ethnicities.id','inclusionCriteria.genders.id','inclusionCriteria.locations.id','inclusionCriteria.phenotypicConditions.featureType.id','inclusionCriteria.phenotypicConditions.severity.id']
                    insert_found_terms(cohorts, cohorts_fields)
                    for alphanumeric_term in alphanumeric_terms_cohorts:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['cohort']
                                            })
                elif entity == 'dataset':
                    datasets_fields=['dataUseConditions.duoDataUse.id']
                    insert_found_terms(datasets, datasets_fields)
                    for alphanumeric_term in alphanumeric_terms_datasets:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['dataset']
                                            })
                elif entity == 'genomicVariant':
                    genomicVariations_fields=['caseLevelData.alleleOrigin.id','caseLevelData.clinicalInterpretations.category.id','caseLevelData.clinicalInterpretations.effect.id','caseLevelData.clinicalInterpretations.evidenceType.id','caseLevelData.id','caseLevelData.phenotypicEffects.category.id','caseLevelData.phenotypicEffects.effect.id','caseLevelData.phenotypicEffects.evidenceType.id','caseLevelData.zygosity.id','identifiers.variantAlternativeIds.id','molecularAttributes.molecularEffects.id','variantLevelData.clinicalInterpretations.category.id','variantLevelData.clinicalInterpretations.effect.id','variantLevelData.clinicalInterpretations.evidenceType.id','variantLevelData.phenotypicEffects.category.id','variantLevelData.phenotypicEffects.effect.id','variantLevelData.phenotypicEffects.evidenceType.id']
                    insert_found_terms(genomicVariations, genomicVariations_fields)
                    for alphanumeric_term in alphanumeric_terms_g_variants:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['genomicVariation']
                                            })
                    insert_zygosity_terms()
                elif entity == 'individual':
                    individuals_fields=['diseases.ageOfOnset.id','diseases.diseaseCode.id','diseases.severity.id','diseases.stage.id','ethnicity.id','exposures.exposureCode.id','exposures.unit.id','geographicOrigin.id','interventionsOrProcedures.ageAtProcedure.id','interventionsOrProcedures.bodySite.id','interventionsOrProcedures.procedureCode.id','measures.assayCode.id','measures.measurementValue.id','measures.measurementValue.typedQuantities.quantity.unit.id','measures.measurementValue.unit.id','measures.observationMoment.id','measures.procedure.bodySite.id','measures.procedure.procedureCode.id','pedigrees.disease.diseaseCode.id','pedigrees.disease.severity.id','pedigrees.disease.stage.id','pedigrees.id','pedigrees.members.role.id','phenotypicFeatures.evidence.evidenceCode.id','phenotypicFeatures.evidence.reference.id','phenotypicFeatures.featureType.id','phenotypicFeatures.modifiers.id','phenotypicFeatures.onset.id','phenotypicFeatures.resolution.id','phenotypicFeatures.severity.id','sex.id','treatments.cumulativeDose.referenceRange.id','treatments.doseIntervals.id','treatments.routeOfAdministration.id','treatments.treatmentCode.id']
                    insert_found_terms(individuals, individuals_fields)
                    for alphanumeric_term in alphanumeric_terms_individuals:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['individual']
                                            })
                elif entity == 'run':
                    runs_fields=['librarySource.id','platformModel.id']
                    insert_found_terms(runs, runs_fields)
                    for alphanumeric_term in alphanumeric_terms_runs:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['run']
                                            })
                elif entity == 'patients':
                    patients_fields=['disease.diagnosis.id' ,'disease.imagingProcedureProtocol.id', 'disease.pathology.id', 'disease.pathologyConfirmation.id', 'disease.treatment.id', 'disease.tumorMetadata.ER.id', 'disease.tumorMetadata.PR.id', 'disease.tumorMetadata.HER2.id', 'disease.tumorMetadata.cancerStageCMCategory.id', 'disease.tumorMetadata.cancerStagePMCategory.id', 'disease.tumorMetadata.histologicGraceGleasonScore.id', 'disease.tumorMetadata.histologicGradeISUP.id', 'disease.tumorMetadata.tumorBIRADSAssesment.id', 'disease.tumorMetadata.tumorPIRADSAssesment.id', 'imageStudy.disease.diagnosis.id' ,'imageStudy.disease.imagingProcedureProtocol.id', 'imageStudy.disease.pathology.id', 'imageStudy.disease.pathologyConfirmation.id', 'imageStudy.disease.treatment.id', 'imageStudy.disease.tumorMetadata.ER.id', 'imageStudy.disease.tumorMetadata.PR.id', 'imageStudy.disease.tumorMetadata.HER2.id', 'imageStudy.disease.tumorMetadata.cancerStageCMCategory.id', 'imageStudy.disease.tumorMetadata.cancerStagePMCategory.id', 'imageStudy.disease.tumorMetadata.histologicGraceGleasonScore.id', 'imageStudy.disease.tumorMetadata.histologicGradeISUP.id', 'imageStudy.disease.tumorMetadata.tumorBIRADSAssesment.id', 'imageStudy.disease.tumorMetadata.tumorPIRADSAssesment.id', 'imageStudy.imageModality.id', 'imageStudy.imageBodyPart.id', 'imageStudy.imageManufacturer.id', 'sex.id']
                    insert_found_terms(patients, patients_fields)
                    for alphanumeric_term in alphanumeric_terms_patients:
                        alphanumterms.append({
                                                'type': 'alphanumeric',
                                                'id': alphanumeric_term,
                                                'scopes': ['patients']
                                            })
                elif entity == 'imagestudies':
                    imagestudies_fields=['disease.diagnosis.id' ,'disease.imagingProcedureProtocol.id', 'disease.pathology.id', 'disease.pathologyConfirmation.id', 'disease.treatment.id', 'disease.tumorMetadata.ER.id', 'disease.tumorMetadata.PR.id', 'disease.tumorMetadata.HER2.id', 'disease.tumorMetadata.cancerStageCMCategory.id', 'disease.tumorMetadata.cancerStagePMCategory.id', 'disease.tumorMetadata.histologicGraceGleasonScore.id', 'disease.tumorMetadata.histologicGradeISUP.id', 'disease.tumorMetadata.tumorBIRADSAssesment.id', 'disease.tumorMetadata.tumorPIRADSAssesment.id', 'imageModality.id', 'imageBodyPart.id', 'imageManufacturer.id']
                    insert_found_terms(imagestudies, imagestudies_fields)
    if alphanumterms != []:
        filtering_terms_.insert_many(alphanumterms)

def find_ontology_terms_used(collection) -> List[Dict]:
    print(collection.name)
    terms_ids = []
    count = collection.estimated_document_count()
    # In case there are more than 50.000 docs, only scan the first 50.000 docs to populate the filtering terms with the ontologies found in these docs
    if count < 50000:
        num_total=count
    else:
        num_total=50000
    i=0
    if count > 50000:
        while i < count:
            xs = collection.find().skip(i).limit(50000)
            for r in tqdm(xs, total=num_total):
                matches = ONTOLOGY_REGEX.findall(str(r))
                icd_matches = ICD_REGEX.findall(str(r))
                for ontology_id, term_id in matches:
                    term = ':'.join([ontology_id, term_id])
                    if term not in terms_ids:
                        terms_ids.append(term)
                for ontology_id, term_id in icd_matches:
                    term = ':'.join([ontology_id, term_id])
                    if term not in terms_ids:
                        terms_ids.append(term)
            i += 10000
            if i > 80000:
                break
            print(i)
    else:
        xs = collection.find().skip(0).limit(50000)
        for r in tqdm(xs, total=num_total):
            matches = ONTOLOGY_REGEX.findall(str(r))
            icd_matches = ICD_REGEX.findall(str(r))
            for ontology_id, term_id in matches:
                term = ':'.join([ontology_id, term_id])
                if term not in terms_ids:
                    terms_ids.append(term) 
            for ontology_id, term_id in icd_matches:
                term = ':'.join([ontology_id, term_id])
                if term not in terms_ids:
                    terms_ids.append(term)
    return terms_ids



def get_filtering_object(terms_ids: list, collection, fields):
    """
    Create the filtering term object Beacon v2 compliant with the fields/properties and labels found when scanning the database storing them in an array of terms.
    """
    terms = []
    list_of_ontologies=[]
    #ontologies = dict()
    for onto in terms_ids:
        ontology = onto.split(':')
        ontology_id = ontology[0]
        term_id = ontology[1]
        #if ontology_id not in ontologies:
            #ontologies[ontology_id] = load_ontology(ontology_id)
        if ontology_id.isupper():
            field_dict = get_ontology_field_name(ontology_id, term_id, collection.name, fields)
        else:
            continue
        try:
            field = field_dict['field']
            label = field_dict['label']
            value_id=None
            if 'measurements.assayCode' in field:
                value_id = label
            if 'measures.assayCode' in field:
                value_id = label
            ontology_label = label
            if field is not None:
                if onto not in list_of_ontologies:
                    list_of_ontologies.append(onto)
                    if collection.name == 'patients' or collection.name == 'collections':
                        colname = collection.name
                    elif collection.name == 'analyses':
                        colname = 'analysis'
                    elif collection.name == 'imagestudies':
                        colname = 'imageStudies'
                    else:
                        colname = collection.name[0:-1]
                    if label:
                        terms.append({
                                        'type': 'ontology',
                                        'id': onto,
                                        'label': ontology_label,
                                        # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                                        #'count': get_ontology_term_count(collection_name, onto),
                                        'scopes': [colname]                 
                                    })

                        terms.append({
                                                'type': 'alphanumeric',
                                                'id': field,
                                                # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                                                #'count': get_ontology_term_count(collection_name, onto),
                                                'scopes': [colname]     
                                            })
                        terms.append({
                                        'type': 'custom',
                                        'id': '{}:{}'.format(field,label),
                                        # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                                        #'count': get_ontology_term_count(collection_name, onto),
                                        'scopes': [colname]                        
                                    })
                    if value_id is not None:
                        terms.append({
                                                'type': 'alphanumeric',
                                                'id': value_id,
                                                # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                                                #'count': get_ontology_term_count(collection_name, onto),
                                                'scopes': [colname]     
                                            })

                print(terms)
        except Exception:
            pass

    return terms


def get_alphanumeric_term_count(collection_name: str, key: str) -> int:
    return len(client[dbname]\
        .get_collection(collection_name)\
        .distinct(key))

def get_properties_of_document(document, prefix="") -> List[str]:
    properties = []
    if document is None or isinstance(document, str) or isinstance(document, int):
        return []
    elif isinstance(document, list):
        for elem in document:
            properties += get_properties_of_document(elem, prefix)
    elif isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                continue
            elif value is None:
                properties.append(prefix + '.' + key if prefix else key)
            elif isinstance(value, int):
                properties.append(prefix + '.' + key if prefix else key)
            elif isinstance(value, str):
                properties.append(prefix + '.' + key if prefix else key)
            elif isinstance(value, list):
                properties += get_properties_of_document(value, prefix + '.' + key if prefix else key)
            elif isinstance(value, dict):
                properties += get_properties_of_document(value, prefix + '.' + key if prefix else key)
            else:
                print('Unknown type:', value, ' (', type(value), ')')
                exit(0)
    else:
        print('Unknown type2:', document, ' (', type(document), ')')
        exit(0)
    return properties

def merge_ontology_terms():
    """
    Scan all the filtering terms of type ontology found and remove the duplicated ones.
    """
    filtering_terms = filtering_terms_.find({"type": "ontology"})
    array_of_ids=[]
    repeated_ids=[]
    new_terms=[]
    for filtering_term in filtering_terms:
        new_id=filtering_term["id"]
        if new_id not in array_of_ids:
            array_of_ids.append(new_id)
        else:
            repeated_ids.append(new_id)
    #print("repeated_ids are {}".format(repeated_ids))
    for repeated_id in repeated_ids:
        repeated_terms = filtering_terms_.find({"id": repeated_id, "type": "ontology"})
        array_of_scopes=[]
        for repeated_term in repeated_terms:
            #print(repeated_term)
            id=repeated_term["id"]
            label=repeated_term["label"]
            if repeated_term['scopes'] != []:
                if repeated_term['scopes'][0] not in array_of_scopes:
                    array_of_scopes.append(repeated_term['scopes'][0])
        if array_of_scopes != []:
            new_terms.append({
                'type': 'ontology',
                'id': id,
                'label': label,
                # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                #'count': get_ontology_term_count(collection_name, onto),
                'scopes': array_of_scopes        
                        })
        filtering_terms_.delete_many({"id": repeated_id})
    if new_terms != []:
        filtering_terms_.insert_many(new_terms)
        
    
def merge_alphanumeric_terms():
    """
    Scan all the filtering terms of type alphanumeric found and remove the duplicated ones.
    """
    filtering_terms = filtering_terms_.find({"type": "alphanumeric"})
    array_of_ids=[]
    repeated_ids=[]
    new_terms=[]
    for filtering_term in filtering_terms:
        new_id=filtering_term["id"]
        if new_id not in array_of_ids:
            array_of_ids.append(new_id)
        else:
            repeated_ids.append(new_id)
    #print("repeated_ids are {}".format(repeated_ids))
    for repeated_id in repeated_ids:
        repeated_terms = filtering_terms_.find({"id": repeated_id, "type": "alphanumeric"})
        array_of_scopes=[]
        for repeated_term in repeated_terms:
            #print(repeated_term)
            id=repeated_term["id"]
            if repeated_term['scopes'] != []:
                if repeated_term['scopes'][0] not in array_of_scopes:
                    array_of_scopes.append(repeated_term['scopes'][0])
        if array_of_scopes != []:
            new_terms.append({
                'type': 'alphanumeric',
                'id': id,
                # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                #'count': get_ontology_term_count(collection_name, onto),
                'scopes': array_of_scopes        
                        })
        filtering_terms_.delete_many({"id": repeated_id})
    if new_terms != []:
        filtering_terms_.insert_many(new_terms)
    
def merge_custom_terms():
    """
    Scan all the filtering terms of type custom found and remove the duplicated ones.
    """
    filtering_terms = filtering_terms_.find({"type": "custom"})
    array_of_ids=[]
    repeated_ids=[]
    new_terms=[]
    for filtering_term in filtering_terms:
        new_id=filtering_term["id"]
        if new_id not in array_of_ids:
            array_of_ids.append(new_id)
        else:
            repeated_ids.append(new_id)
    #print("repeated_ids are {}".format(repeated_ids))
    for repeated_id in repeated_ids:
        repeated_terms = filtering_terms_.find({"id": repeated_id, "type": "custom"})
        array_of_scopes=[]
        for repeated_term in repeated_terms:
            #print(repeated_term)
            id=repeated_term["id"]
            if repeated_term['scopes'] != []:
                if repeated_term['scopes'][0] not in array_of_scopes:
                    array_of_scopes.append(repeated_term['scopes'][0])
        if array_of_scopes != []:
            new_terms.append({
                'type': 'custom',
                'id': id,
                # TODO: Use conf.py -> beaconGranularity to not disclouse counts in the filtering terms
                #'count': get_ontology_term_count(collection_name, onto),
                'scopes': array_of_scopes        
                        })
        filtering_terms_.delete_many({"id": repeated_id})
    if new_terms != []:
        filtering_terms_.insert_many(new_terms)

def insert_zygosity_terms():
    heterozygous={"id": "GENO:0000458",
     "label": "simple heterozygous",
     "type": "ontology",
     "scopes": ["genomicVariation"]}
    homozygous={"id": "GENO:0000136",
     "label": "homozygous",
     "type": "ontology",
     "scopes": ["genomicVariation"]}
    zygosity_terms=[]
    zygosity_terms.append(heterozygous)
    zygosity_terms.append(homozygous)
    filtering_terms_.insert_many(zygosity_terms)
    




insert_all_ontology_terms_used()
merge_ontology_terms()
merge_alphanumeric_terms()
merge_custom_terms()
