import progressbar
from beacon.connections.mongo.client import get_client
import requests
import tqdm
from beacon.connections.mongo.conf import database_name

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

def get_all_ancestors_descendants(ontology_id, code):

    ancestors_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/ancestors?id={ontology_id}:{code}"
    ancestors_data = requests.get(ancestors_url).json()
    if "_embedded" in ancestors_data:
        list_of_ancestors_full=ancestors_data["_embedded"]["terms"]
        for ancestor in list_of_ancestors_full:
            ancestor_descendants_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/children?id={ancestor['obo_id']}"
            ancestor_descendants_data = requests.get(ancestor_descendants_url).json()
            if "_embedded" in ancestor_descendants_data:
                list_of_ancestor_descendants_full=ancestor_descendants_data["_embedded"]["terms"]
                list_of_ancestors_descendants=[]
                is_list=False
                for ancestor_descendant in list_of_ancestor_descendants_full:
                    list_of_ancestors_descendants.append(ancestor_descendant["obo_id"])
                    if ancestor_descendant["obo_id"] == ontology_id+":"+code:
                        is_list=True
                if is_list==True:
                    return list_of_ancestors_descendants, list_of_ancestors_full
    else:
        return None, None
    return None, list_of_ancestors_full

def get_descendants_and_similarities():
    list_of_ontology_families=[]
    dict_of_ontology_families={}
    client=get_client()
    try:
        client[database_name].drop_collection("similarities")
    except Exception:
        client[database_name].create_collection(name="similarities")
    try:
        client[database_name].validate_collection("similarities")
    except Exception:
        db=client[database_name].create_collection(name="similarities")
    filtering_docs=client[database_name].filtering_terms.find({"type": "ontology"})
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
    i=0
    j=0
    for ontology_id, ontology_codes_list in dict_of_ontology_families.items():
        pbar = tqdm.tqdm(total=len(ontology_codes_list))
        list_of_existing_descendants = []
        for code in ontology_codes_list:
            definitive_similarity_high=[]
            definitive_similarity_medium=[]
            definitive_similarity_low=[]
            #url = f"https://api-evsrest.nci.nih.gov/api/v1/concept/{ontology_id.lower()}/{code}/descendants"
            url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology_id.lower()}/descendants?id={ontology_id}:{code}"
            data = requests.get(url).json()
            if "_embedded" in data:
                list_of_descendants_full=data["_embedded"]["terms"]
                for descendant in list_of_descendants_full:
                    if descendant["obo_id"] in ontology_codes_list:
                        list_of_existing_descendants.append(descendant["obo_id"])
            similarity_high, similarity_low = get_all_ancestors_descendants(ontology_id, code)

            if similarity_high == None:
                similarity_medium = None
                pass
            else:
                similarity_high.remove(ontology_id+":"+code)
                definitive_similarity_high=discard_non_scanned_ontologies(similarity_high, ontology_codes_list)
                similarity_medium_list=[]
                for similar_high_ontology in definitive_similarity_high:
                    split_similar_high = similar_high_ontology.split(":")
                    similarity_medium, cousins_ancestors_list = get_all_ancestors_descendants(split_similar_high[0], split_similar_high[1])
                    if similarity_medium is not None:
                        if similar_high_ontology in similarity_medium:
                            similarity_medium.remove(similar_high_ontology)
                        if ontology_id+":"+code in similarity_medium:
                            similarity_medium.remove(ontology_id+":"+code)
                        for medium_ontology in similarity_medium:
                            similarity_medium_list.append(medium_ontology)

                definitive_similarity_medium=discard_non_scanned_ontologies(similarity_medium_list, ontology_codes_list)
            similarity_low_corrected=[]
            if similarity_low is not None:
                for low_similar_ontology in similarity_low:
                    similarity_low_corrected.append(low_similar_ontology["obo_id"])
                definitive_similarity_low=discard_non_scanned_ontologies(similarity_low_corrected, ontology_codes_list)

            definitive_similarity_medium=definitive_similarity_high+definitive_similarity_medium
            definitive_similarity_low=definitive_similarity_medium+definitive_similarity_low
            print(f"\n===== {ontology_id}:{code} =====")
            print('-----DESCENDANTS-----')
            print(list_of_existing_descendants)
            print('-----SIMILARITY_HIGH-----')
            print(definitive_similarity_high)
            print('-----SIMILARITY_MEDIUM-----')
            print(definitive_similarity_medium)
            print('-----SIMILARITY_LOW-----')
            print(definitive_similarity_low)

            dict={}
            if list_of_existing_descendants != [] or definitive_similarity_low != []:
                dict['id']=ontology_id+":"+code
                dict['descendants']=list_of_existing_descendants
                dict['similarity_high']=definitive_similarity_high
                dict['similarity_medium']=definitive_similarity_medium
                dict['similarity_low']=definitive_similarity_low
                
                client[database_name].similarities.insert_one(dict)
                j+=1

            pbar.update(1)
            i+=1
    print("succesfully retrieved {} terms relationships and inserted {} of those".format(i,j))
        
    
get_descendants_and_similarities()
    
