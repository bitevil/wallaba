from src.pgmethods import PgSQLMethods
import redis
import os

PRIMARY =  os.getenv("IS_PG_PRIMARY")
DB_REFEREE =  os.getenv("DB_REFEREE")
HOSTNAME =  os.getenv("HOSTNAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
PGDATA = os.getenv("PGDATA")

redis_client = redis.Redis(host='redis', port=6379, db=0)

nodes = str(redis_client.get('nodes')).split(",")

for node in nodes:
    pgs = PgSQLMethods(user=POSTGRES_USER,secret=POSTGRES_PASSWORD,hostname=HOSTNAME,port="5432,5433",database="public")
    print(f"Is node {node} availible {pgs.health_check()}; is replica {pgs.is_replica()}")

print(PgSQLMethods(user=POSTGRES_USER,secret=POSTGRES_PASSWORD,hostname=",".join(nodes),port="5432,5433",database="public").bench(100000))

for node in nodes:
    pgs = PgSQLMethods(user=POSTGRES_USER,secret=POSTGRES_PASSWORD,hostname=HOSTNAME,port="5432,5433",database="public")
    print(f"Is node {node} availible {pgs.health_check()}; is replica {pgs.is_replica()}")