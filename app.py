from flask import Flask
from redis import Redis 
from redis.cluster import RedisCluster
from flask import request
import os
from uuid import uuid4

base_dir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)

CA_CERTIFICATE = os.path.join(base_dir, "testCerts/ca.crt")
CLIENT_CERT = os.path.join(base_dir, "testCerts/client.crt")
CLIENT_KEY = os.path.join(base_dir, "testCerts/client.key")
CLUSTER_PASSWORD = os.environ.get("password")


def redis_connection(password):

    cluster_node = ("192.168.58.4", 6379)

    rc = RedisCluster(
        host=cluster_node[0],
        port=cluster_node[1],
        password=password,
        ssl=True,
        ssl_ca_certs=CA_CERTIFICATE,
        ssl_certfile=CLIENT_CERT,
        ssl_keyfile=CLIENT_KEY
    )

    return rc

@app.route("/", methods=["GET","POST"])
def index():

    node = None
    user_input = None
    if request.method == "POST":
        # Get the user-submitted data from the form
        user_input = request.form["user_input"]

        if user_input is not None and user_input != "":

            database_key = str(uuid4())

            database = redis_connection(CLUSTER_PASSWORD)

            database.set(database_key, user_input)

            hash_slot = database.execute_command("CLUSTER", "KEYSLOT", database_key)

            nodes_info = database.execute_command("CLUSTER", "NODES")

            for node_info in nodes_info.decode().split('\n'):

                node_info = node_info.split(' ')
                node_id = node_info[0]
                slots = node_info[8:]

                for slot_range in slots:

                    start, end = map(int, slot_range.split('-'))

                    if start <= hash_slot <= end:

                        node = node_id

    # HTML form to submit user data
    response = f"""
    <html>
        <title>Redis Cluster Tutorial</title>
        <body>
            <h1>Running Redis on Scale 101</h1>
            <form method="post">
                <input type="text" name="user_input" placeholder="Enter your name and see to which node its stored">
                <input type="submit" value="Submit">
            </form>

            <p>The {user_input if user_input else ""} was stored in node {node if node is not None else ""} </p>
        </body>
    </html>
    """


    return response

if __name__ == "__main__":

    app.run()
