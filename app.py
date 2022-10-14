import os
import sys
import json
import subprocess
import pandas as pd
from flask_cors import CORS
from pymongo import MongoClient
from flask import Flask, jsonify
from bson.json_util import dumps
from useless_words import useless_words
from dotenv import load_dotenv

load_dotenv()

# from mongo_connect import MONGO_URI

# ============== define app =============
app = Flask(__name__)

# ============== app middleware =========
CORS(app)
app.config['MONGO_CONNECT'] = False


# client = MongoClient(os.getenv("MONGO_URI", f"{MONGO_URI}"))
client = MongoClient(os.getenv("MONGO_URI"))
db = client.jobs_project

# ============== data tranformations ==================


def get_job_titles(skill):
    jobs = db.jobs.find({'stripped_job_description': {'$regex': skill.lower()}}, {
        'stripped_job_description': 0, 'row_num': 0})
    json_jobs = json.loads(dumps(jobs))
    return json_jobs


def make_job_title_cache(string):
    cache = {}
    try:
        for item in get_job_titles(string):
            if item["job_title"] not in cache:
                cache[item["job_title"]] = 1
            else:
                cache[item["job_title"]] += 1
        df = pd.DataFrame(cache.items())
        df.rename(columns={0: "key", 1: "value"}, inplace=True)
        return df.sort_values("value", ascending=False).head(50).to_dict('records')
    except (TypeError, NameError, KeyError) as e:
        print(e)
        return {"msg": e}


def get_job_desc(desc):
    jobs = db.jobs.find({'job_title': {'$regex': desc.lower()}}, {
        'job_title': 0, 'row_num': 0})
    json_jobs = json.loads(dumps(jobs))
    return json_jobs


def make_desc_cache(string):
    words_arr = []
    cache = {}
    try:
        for item in get_job_desc(string):
            is_split = item['stripped_job_description'].split(" ")
            for word in is_split:
                if word != "" and word not in useless_words:
                    words_arr.append(word)
        for item in words_arr:
            if item not in cache:
                cache[item] = 1
            else:
                cache[item] += 1
        df = pd.DataFrame(cache.items())
        df.rename(columns={0: "key", 1: "value"}, inplace=True)
        return df.sort_values("value", ascending=False).head(50).to_dict('records')
    except:
        return {"msg": "You broke it"}


# print(make_desc_cache("Analyst"))
# print(make_job_title_cache("integration"))

# ================= view routes ================


# @app.route("/")
# def home():
#     return render_template('index.html')


# @app.route("/search_skill")
# def search_skill_view():
#     return render_template("search_skill.html")


# @app.route("/search_job_title")
# def search_job_title_view():
#     return render_template("search_job_title.html")


# ==================== api routes =============
@app.route("/", methods=["GET"])
def home():
    return jsonify(data="hello")


@app.route("/api/search_skill/<skill>", methods=["GET"])
def search_skill(skill):
    return jsonify(data=make_job_title_cache(skill))


@app.route("/api/search_job_title/<title>", methods=["GET"])
def search_job_title(title):
    return jsonify(data=make_desc_cache(title))


if __name__ == "__main__":
    app.run(debug=True)
