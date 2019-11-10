from flask import Flask, escape, request, render_template
import os
from flask_pymongo import PyMongo
import json
import yaml
from datetime import datetime


app = Flask(__name__)

app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(app)
db = mongo.db

col_items = db['collection_items']
col_names = db['collection_names']


def getData():
    myNames = []
    myData = []
    for item in col_names.find({}, {"_id": 0}):
        qry = {"name": item["name"]}
        occurences = len(list(col_items.find(qry, {"_id": 0, "name": 0})))
        myNames.append(item['name'])
        myData.append(occurences)
        print(f"name: {item['name']}, occurences: {occurences}")
    data = {}
    data['names'] = myNames
    data['data'] = myData
    return data

@app.route('/')
def default():
    data = getData()
    myNames = data["names"]
    myData = data["data"]
    return render_template('index.html', myNames=json.dumps(myNames), myData=json.dumps(myData))

    # return 'Hello World!!!!'

@app.route('/rmAll')
def rmAll():
    for col_name in db.list_collection_names():
        db[col_name].drop()
    return "Done!"


@app.route('/update',methods=['GET'])
def update():
    name = request.args.get('name')
    if col_names.find_one({"name": name}) == None:
        col_names.insert_one({"name": name})
    print("update")
    return json.dumps(getData())

@app.route('/background_process_test',methods=['GET'])
def background_process_test():
    idx = request.args.get('idx')
    data = getData()

    col_item = {}
    col_item['name'] = data['names'][int(idx)]
    col_item['time'] = datetime.timestamp(datetime.now())
    col_items.insert_one(col_item)

    return json.dumps(getData())