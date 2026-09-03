import obonet
import networkx
import os
import urllib.request
from urllib.error import HTTPError
import progressbar
from beacon.connections.mongo.client import get_client
import requests
import json

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

def discard_non_scanned_ontologies(list_of_all_ontologies, ontology_codes_list):
    definitive_list=[]
    for similar_ontology in list_of_all_ontologies:
        if similar_ontology in ontology_codes_list:
            definitive_list.append(similar_ontology)
    return definitive_list

def get_all_ancestors_descendants(ontology_id, code, data):
    similarity_high=[]
    ancestors_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/ancestors?id={ontology_id}:{code}"
    ancestors_data = requests.get(ancestors_url).json()
    if "_embedded" in ancestors_data:
        list_of_ancestors_full=data["_embedded"]["terms"]
        for ancestor in list_of_ancestors_full:
            ancestor_descendants_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/ancestors?id={ancestor["obo_id"]}"
            ancestor_descendants_data = requests.get(ancestor_descendants_url).json()
            if "_embedded" in ancestor_descendants_data:
                list_of_ancestor_descendants_full=data["_embedded"]["terms"]
                for ancestor_descendant in list_of_ancestor_descendants_full:
                    if ancestor_descendant["obo_id"] == ontology_id+":"+code:
                        similarity_high = list_of_ancestor_descendants_full
                        return similarity_high, list_of_ancestor_descendants_full

def get_descendants_and_similarities():
    list_of_ontology_families=[]
    dict_of_ontology_families={}
    client=get_client()
    try:
        client['beacon'].drop_collection("similarities")
    except Exception:
        client['beacon'].create_collection(name="similarities")
    try:
        client['beacon'].validate_collection("similarities")
    except Exception:
        db=client['beacon'].create_collection(name="similarities")
    filtering_docs=client['beacon'].filtering_terms.find({"type": "ontology"})
    array_of_ontologies=[]
    for ft_doc in filtering_docs:
        if ft_doc["id"] not in array_of_ontologies:
            array_of_ontologies.append(ft_doc["id"])
    for ontology in array_of_ontologies:
        ontology_list = ontology.split(':')
        if ontology_list[0] not in dict_of_ontology_families:
            dict_of_ontology_families[ontology_list[0]]=[ontology_list[1]]
        else:
            dict_of_ontology_families[ontology_list[0]].append(ontology_list[1])
    for ontology_id, ontology_codes_list in dict_of_ontology_families.items():
        list_of_existing_descendants = []
        for code in ontology_codes_list:
            #url = f"https://api-evsrest.nci.nih.gov/api/v1/concept/{ontology_id.lower()}/{code}/descendants"
            url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/descendants?id={ontology_id}:{code}"
            data = requests.get(url).json()
            if "_embedded" in data:
                list_of_descendants_full=data["_embedded"]["terms"]
                for descendant in list_of_descendants_full:
                    if descendant["obo_id"] in ontology_codes_list:
                        list_of_existing_descendants.append(descendant["obo_id"])

            similarity_high, similarity_low = get_all_ancestors_descendants(ontology_id, code, data)
            similarity_high.remove[ontology_id+":"+code]
            definitive_similarity_high=discard_non_scanned_ontologies(similarity_high, ontology_codes_list)

            for similar_high_ontology in definitive_similarity_high:
                split_similar_high = similar_high_ontology.split(":")
                similarity_medium, cousins_ancestors_list = get_all_ancestors_descendants(split_similar_high[0], split_similar_high[1], data)
                similarity_medium.remove(similar_high_ontology)

            definitive_similarity_medium=discard_non_scanned_ontologies(similarity_medium, ontology_codes_list)

            definitive_similarity_low=discard_non_scanned_ontologies(similarity_low, ontology_codes_list)


            print(f"\n===== {ontology_id}:{code} =====")
            print('-----DESCENDANTS-----')
            print(list_of_existing_descendants)
            print('-----SIMILARITY_HIGH-----')
            print(definitive_similarity_high)
            print('-----SIMILARITY_MEDIUM-----')
            print(definitive_similarity_medium)
            print('-----SIMILARITY_LOW-----')
            print(definitive_similarity_low)
            """
            dict={}
            dict['id']=ontology
            dict['descendants']=descendants
            dict['similarity_high']=similarity_high
            dict['similarity_medium']=similarity_medium
            dict['similarity_low']=similarity_low
            
            client['beacon'].similarities.insert_one(dict)
            """
    print("succesfully retrieved descendants from {}".format(ontology))
        
    
get_descendants_and_similarities()
    
