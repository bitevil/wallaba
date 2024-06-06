from flask import Flask
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
from src.pgmethods import PgSQLMethods
import json
import requests
import logging
import redis
 

redis_client = redis.Redis(host='redis', port=6379, db=0)

redis_client.set('nodes', json.dumps([]))
redis_client.set('primary', json.dumps(""))

app = Flask("referee")
logger = logging.getLogger(__name__)

def check_nodes():
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    nodes = json.loads(redis_client.get('nodes'))
    primary = json.loads(redis_client.get('primary'))
    logging.warn(f'{nodes} to check;;; {primary} is primary now')
    if len(nodes) == 0:
        return
    if primary == "":
        logging.warn(f"Can't find primary node!!!")
        return
    for node in nodes:
        try:
            r = requests.get(f'http://{node}:5000/check')
            logging.warning(f'\n\n\n\n\n {r.json()} \n\n\n\n\n\ncheck - OK')
            if r.json()["status"] != 200:
                raise
            logging.info(f'{node} check - OK')
        except Exception as e:
            logging.critical(f'{node} check - ERR {e}')
            nodes.remove(node)
            if node == primary:
                scheduler.pause()
                primary = nodes[0]
                # promote [0] node
                r = requests.post(f'http://{primary}:5000/promote')
                logging.warn(f"Node {primary} promoted! {r.json()}")
                scheduler.resume()
            redis_client.set('primary', json.dumps(primary))
            redis_client.set('nodes', json.dumps(nodes))


scheduler = BackgroundScheduler()
scheduler.add_job(func=check_nodes, trigger="interval", seconds=1)
scheduler.start()

@app.route('/check')
def check():
    return {"status": 200}

@app.route('/primary')
def get_primary():
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    primary = json.loads(redis_client.get('primary'))
    return {"status": 200, "primary": primary}

@app.route('/addnode', methods = ['POST'])
def addnode():
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    nodes = json.loads(redis_client.get('nodes'))
    primary = json.loads(redis_client.get('primary'))
    data = request.json
    logging.info(f'Started {data}')
    if data["hostname"] in nodes:
        return {"status": 200, "comment":"Already exists"}
    nodes.append(data["hostname"])
    redis_client.set('nodes', json.dumps(nodes))
    if primary == "":
        if "primary" in data:
            primary = data["hostname"]
            redis_client.set('primary', json.dumps(primary))
            return {"status": 200, "comment":"OK. Primary added!"}

    return {"status": 200, "comment":"OK. Node added!"}

app.run(host='0.0.0.0')