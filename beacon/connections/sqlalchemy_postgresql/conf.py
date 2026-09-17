from dotenv import load_dotenv
import os

postgres_conf = "beacon/connections/postgres/conf.env"
load_dotenv(postgres_conf, override=True)

database_host = os.getenv('database_host', 'postgres')
database_port = os.getenv('database_port', str(5432))
database_user = os.getenv('database_user', 'postgres')
database_password = os.getenv('database_password', 'your_secure_password')
database_name = os.getenv('database_name', 'beacon')