import os
import yaml
from django.http import JsonResponse

def default_view(request):
    params =request.GET.urlencode()
    print(params, flush=True)
    params_splitted = params.split("%")
    dirs = os.listdir("/home/app/web/beacon/models")
    entry_types = []

    for param in params_splitted:
        if param in dirs:
            model_found=param
            break

    print(model_found, flush=True)

    with open("/home/app/web/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)

    for folder in dirs:
        subdirs = os.listdir("/home/app/web/beacon/models/"+folder)
        if folder == model_found:
            if folder in models_confile:
                if models_confile[folder]["model_enabled"] == False:
                    continue
            # Go over the conf for the entry types of the models enabled
            if "conf" in subdirs:
                path = (
                    "/home/app/web/beacon/models/"
                    f"{folder}/conf/entry_types"
                )
                for filename in os.listdir(path):

                    if filename.endswith(".yml"):
                        entry_type = filename[:-4]
                        entry_types.append(entry_type)
            else:
                for subfolder in subdirs:
                    if subfolder not in ['validator', 'conf', 'connections']:
                        underdirs = os.listdir("/home/app/web/beacon/models/"+folder+"/"+subfolder)
                        if folder  == model_found:
                            if folder+'/'+subfolder in models_confile:
                                if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                                    continue
                            # Go over the conf for the entry types of the models enabled
                            if "conf" in underdirs:
                                path = (
                                    "/home/app/web/beacon/models/"
                                    f"{folder}/{subfolder}/conf/entry_types"
                                )
                                for filename in os.listdir(path):

                                    if filename.endswith(".yml"):
                                        entry_type = filename[:-4]
                                        entry_types.append(entry_type)
    print(entry_types, flush=True)
    
    return JsonResponse({"choices": entry_types})
