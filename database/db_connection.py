import psycopg2
from psycopg2.extensions import connection

from config.docker_helper import is_docker_container
from constants import DATABASE_NAME, POSTGRES_USER, POSTGRES_PASSWORD
from env_data.get_env_value import get_env_value


def get_db_connection() -> connection:
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user=get_env_value(POSTGRES_USER),
        password=get_env_value(POSTGRES_PASSWORD),
        host=get_pg_url()
    )

def get_pg_url() -> str:
    return 'postgres' if is_docker_container() else 'localhost'