import sys
import yaml

version = sys.argv[1]

with open("beacon/conf/api_version.yml") as f:
    api_version = yaml.safe_load(f)

api_version["api_version"] = version

with open("beacon/conf/api_version.yml", "w") as f:
    yaml.safe_dump(api_version, f, sort_keys=False)

print(f"API version updated to {version}")