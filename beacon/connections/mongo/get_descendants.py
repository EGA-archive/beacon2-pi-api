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

def get_descendants_and_similarities():
    list_of_ontology_families=[]
    similarity_high=[]
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
            parent=None
            #url = f"https://api-evsrest.nci.nih.gov/api/v1/concept/{ontology_id.lower()}/{code}/descendants"
            url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/descendants?id={ontology_id}:{code}"
            data = requests.get(url).json()
            if "_embedded" in data:
                list_of_descendants_full=data["_embedded"]["terms"]
                for descendant in list_of_descendants_full:
                    if descendant["obo_id"] in ontology_codes_list:
                        list_of_existing_descendants.append(descendant["obo_id"])

            print(f"\n===== {ontology_id}:{code} =====")
            print(list_of_existing_descendants)

            ancestors_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/descendants?id={ontology_id}:{code}"
            ancestors_data = requests.get(ancestors_url).json()
            if "_embedded" in ancestors_data:
                list_of_ancestors_full=data["_embedded"]["terms"]
                for ancestor in list_of_ancestors_full:
                    ancestor_descendants_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/descendants?id={ancestor["obo_id"]}"
                    ancestor_descendants_data = requests.get(ancestor_descendants_url).json()
                    if "_embedded" in ancestor_descendants_data:
                        list_of_ancestor_descendants_full=data["_embedded"]["terms"]
                        for ancestor_descendant in list_of_ancestor_descendants_full:
                            if ancestor_descendant["obo_id"] == ontology_id+":"+code:
                                parent = ancestor_descendant["obo_id"]
                                similarity_high = list_of_ancestor_descendants_full
                                break
                similarity_high.remove[ontology_id+":"+code]
                definitive_similarity_high=[]
                for similar_high_ontology in similarity_high:
                    if similar_high_ontology in ontology_codes_list:
                        definitive_similarity_high.append(similar_high_ontology)
            

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
    
