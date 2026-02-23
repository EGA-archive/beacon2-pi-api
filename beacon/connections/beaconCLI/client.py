import paramiko
from beacon.connections.beaconCLI import conf
from beacon.exceptions.exceptions import DatabaseIsDown

def create_ssh(host, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(host, username=username, password=password)
    return ssh

def get_client():
    try:
        client = create_ssh(host=conf.host, username=conf.username, password=conf.password)
        return client
    except Exception as e:
        pass
        #raise DatabaseIsDown(str(e))