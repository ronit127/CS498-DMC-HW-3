from flask import Flask, request, jsonify
import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["ev_db"]
base_collection = db["vehicles"]


# test
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running"})


# 1. fast but unsafe write
@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    data = request.json

    collection = base_collection.with_options(
        write_concern=WriteConcern(w=1)
    )

    result = collection.insert_one(data)

    return jsonify({"id": str(result.inserted_id)})

# 2. highly durable
@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    data = request.json

    collection = base_collection.with_options(
        write_concern=WriteConcern(w="majority")
    )

    result = collection.insert_one(data)

    return jsonify({"id": str(result.inserted_id)})


# 3. strongly consistent read
@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    collection = base_collection.with_options(
        read_preference=ReadPreference.PRIMARY
    )

    count = collection.count_documents({"Make": "TESLA"})

    return jsonify({"count": count})


# 4. eventually consistent read
@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():
    collection = base_collection.with_options(
        read_preference=ReadPreference.SECONDARY_PREFERRED
    )

    count = collection.count_documents({"Make": "BMW"})
        
    return jsonify({"count": count})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)