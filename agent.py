from flask import Flask
from flask import request
import subprocess, sys
import json
import requests
import os
import time
import logging
from src.pgmethods import PgSQLMethods

app = Flask("agent")
logger = logging.getLogger(__name__)

PRIMARY =  os.getenv("IS_PG_PRIMARY")
DB_REFEREE =  os.getenv("DB_REFEREE")
HOSTNAME =  os.getenv("HOSTNAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
PGDATA = os.getenv("PGDATA")

while 1:
    time.sleep(1)
    try:
        json = {
            "hostname": os.getenv("HOSTNAME"),
        }
        prt = os.getenv("IS_PG_PRIMARY")
        if prt == "PRIMARY":
            json["primary"] = "primary"
            subprocess.call("chmod +x ./setup-replication.sh", shell=True)
            subprocess.call("./setup-replication.sh", shell=True)
        else:
            rf = os.getenv("DB_REFEREE")
            r = requests.get("http://{}:5000/primary".format(rf))
            target = r.json()["primary"]
            subprocess.call("export REPLICATE_FROM={}".format(target), shell=True)
            subprocess.call("chmod +x ./setup-replication.sh", shell=True)
            subprocess.call("./setup-replication.sh", shell=True)
        rf = os.getenv("DB_REFEREE")
        r = requests.post('http://{}:5000/addnode'.format(rf),json=json)
        logger.info("ADD Node complete! {}".format(r))
        if r.json()["status"] != 200:
            raise
        break
    except Exception as e:
        logger.warn("ADD Node to referee fail! {}".format(e))

@app.route('/check')
def check():
    try:
        h = PgSQLMethods(user=os.getenv("POSTGRES_USER"),secret=os.getenv("POSTGRES_PASSWORD"),hostname="localhost",port=os.getenv("PG_PORT"),database="public").e__health_check()
        logging.warning("\n\n\n"+str(h)+"\n\n\n")
        if h == True:
            return {"status": 200}
        else:
            return {"status": 400}
    except Exception as e:
        return {"status": 400, "e":str(e)}

@app.route('/promote', methods = ['POST'])
def promote():
    try:
        ##subprocess.check_output(f"su postgres -c 'pg_ctl -D {os.getenv("PGDATA")} promote'", shell = True, executable = "/bin/sh", stderr = subprocess.STDOUT)
        subprocess.call("touch /tmp/promote_file", shell=True)
        return {"status": 200}
    except:
        return {"status": 500}

@app.route('/kill', methods = ['POST'])
def kill():
    subprocess.call("exit 0", shell=True)
    return {"status": 200}

app.run(host='0.0.0.0')
