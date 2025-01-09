import obonet
import networkx
import os
from typing import List, Dict, Optional
import urllib.request
from urllib.error import HTTPError
import progressbar
from pymongo.mongo_client import MongoClient
import os



import conf


if conf.database_cluster:
    uri = "mongodb+srv://{}:{}@{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
        conf.database_user,
        conf.database_password,
        conf.database_host
    )
else:
    uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
        conf.database_user,
        conf.database_password,
        conf.database_host,
        conf.database_port,
        conf.database_name,
        conf.database_auth_source
    )

if os.path.isfile(conf.database_certificate):
    uri += '&tls=true&tlsCertificateKeyFile={}'.format(conf.database_certificate)
    if os.path.isfile(conf.database_cafile):
        uri += '&tlsCAFile={}'.format(conf.database_cafile)

client = MongoClient(uri)

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

def load_ontology(ontology_id: str):
    if ontology_id.isalpha():
        print(ontology_id)
        url_alt = "https://www.ebi.ac.uk/efo/EFO.obo"
        url = "http://purl.obolibrary.org/obo/{}.obo".format(ontology_id.lower())
        path = "/beacon/connections/mongo/ontologies/{}.obo".format(ontology_id)
        try:
            if not os.path.exists(path):
                full_path = os.path.realpath(__file__)
                print(full_path)
                urllib.request.urlretrieve(url, path, MyProgressBar())
        except HTTPError:
            # TODO: Handle error
            #print("ERROR", HTTPError)
            pass
        except ValueError:
            #print("ERROR", ValueError)
            pass
        except Exception:
            pass
        try:
            #print (os.stat(path).st_size)
            if os.stat(path).st_size == 0:
                try:
                    urllib.request.urlretrieve(url_alt, path, MyProgressBar())
                except HTTPError:
                    # TODO: Handle error
                    #print("ERROR", HTTPError)
                    pass
                except ValueError:
                    #print("ERROR", ValueError)
                    pass
        except Exception:
                pass
    return '{}'.format(ontology_id)


def get_descendants_and_similarities():
    try:
        client.beacon.drop_collection("similarities")
    except Exception:
        client.beacon.create_collection(name="similarities")
    try:
        client.beacon.validate_collection("similarities")
    except Exception:
        db=client.beacon.create_collection(name="similarities")
    filtering_docs=client.beacon.filtering_terms.find({"type": "ontology"})
    array_of_ontologies=[]
    for ft_doc in filtering_docs:
        if ft_doc["id"] not in array_of_ontologies:
            array_of_ontologies.append(ft_doc["id"])
    for ontology in array_of_ontologies:
        ontology_list = ontology.split(':')
        load_ontology(ontology_list[0])    
        url = "/beacon/connections/mongo/ontologies/{}.obo".format(ontology_list[0].lower())
        list_of_cousins = []
        list_of_brothers = []
        list_of_uncles = []
        list_of_grandpas = []
        url_alt = "https://www.ebi.ac.uk/efo/EFO.obo"
        try:
            graph = obonet.read_obo(url)
        except Exception:
            graph = obonet.read_obo(url_alt)
        try:
            descendants = networkx.ancestors(graph, ontology)
        except Exception:
            descendants = ''
        descendants=list(descendants)

        print(descendants)


        try:
            tree = [n for n in graph.successors(ontology)]
            for onto in tree:
                predecessors = [n for n in graph.successors(onto)]
                successors = [n for n in graph.predecessors(onto)]
                list_of_brothers.append(successors)
                list_of_grandpas.append(predecessors)
            similarity_high=[]
            similarity_medium=[]
            similarity_low=[]
            for llista in list_of_grandpas:
                for item in llista:
                    uncles = [n for n in graph.predecessors(item)]
                    list_of_uncles.append(uncles)
                    for uncle in uncles:
                        cousins = [n for n in graph.predecessors(uncle)]
                        if ontology not in cousins:
                            list_of_cousins.append(cousins)

            for llista in list_of_brothers:
                for item in llista:
                    similarity_high.append(item)
                    similarity_medium.append(item)
                    similarity_low.append(item)

            for llista in list_of_cousins:
                for item in llista:
                    similarity_medium.append(item)
                    similarity_low.append(item)
            
            for llista in list_of_uncles:
                for item in llista:
                    similarity_low.append(item)

        except Exception:
            similarity_high=[]
            similarity_medium=[]
            similarity_low=[]

        dict={}
        dict['id']=ontology
        dict['descendants']=descendants
        dict['similarity_high']=similarity_high
        dict['similarity_medium']=similarity_medium
        dict['similarity_low']=similarity_low
        
        client.beacon.similarities.insert_one(dict)
        print("succesfully retrieved descendants from {}".format(ontology))
        
    
get_descendants_and_similarities()
    
