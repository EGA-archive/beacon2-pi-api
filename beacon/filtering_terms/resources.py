import json

with open("beacon/filtering_terms/resources.json") as resources_file:
    try:
        resources = json.load(resources_file)
    except Exception:
        resources = None