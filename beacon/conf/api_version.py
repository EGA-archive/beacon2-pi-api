import subprocess
import yaml


repo_url = 'https://github.com/EGA-archive/beacon2-pi-api.git'
current_branch=subprocess.check_output(["git",
                                        "rev-parse",
                                        "--abbrev-ref",
                                        "HEAD"])
current_branch_string='refs/heads/'+str(current_branch.decode("utf-8"))
current_branch_string=current_branch_string.replace("\n", "")
output_lines = subprocess.check_output(
    [
        "git",
        "ls-remote",
        repo_url,
        "rev-parse",
        "--short",
        "sort=committerdate",
        "HEAD",
        current_branch_string

    ],
    encoding="utf-8",
).splitlines()


print(output_lines)

line_ref = output_lines[1].rpartition("/")[0]

last_line_ref=line_ref[0:7]

last_line_ref="v2.0-"+last_line_ref

print(last_line_ref)

with open("beacon/conf/api_version.yml") as api_version_file:
    api_version = yaml.safe_load(api_version_file)

api_version['api_version']=last_line_ref

with open("beacon/conf/api_version.yml", 'w') as out:
    yaml.dump(api_version, out)