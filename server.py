from __future__ import division
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from math import sqrt
from pymongo import MongoClient
from bson import Binary, Code
import json
import requests
from bson.json_util import dumps
client = MongoClient('localhost:27017',username='root',password='ATIhH2s9gqpc')
db=client.admin
collection=db.ratings

def sim_pearson(prefs,p1,p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    n=len(si)
#   print("SI:",si,p1,p2)
    if n==0:
        return 0
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
#   print("n:",n,"sum1",sum1,"sum2",sum2,"sum1sq",sum1Sq,"sum2Sq",sum2Sq,"pSum:",pSum)
    num=abs(pSum-(sum1*sum2/(n+1)))
    den=abs(sqrt((sum1Sq-pow(sum1,2)/(n+1))*(sum2Sq-pow(sum2,2)/(n+1))))
#   print("num:",num,"den:",den)
    if den==0: return 0
    r=num/den
    return r
def getRecommendations(prefs,person):
    totals={}
    simSums={}
    for other in prefs:
        if other==person: continue
        sim=sim_pearson(prefs,person,other)
 #      print("other:",other,"sim:",sim)
        if sim<0: continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                simSums.setdefault(item,0)
                simSums[item]+=sim
#   print("simSums:",simSums)
    rankings=[(total/simSums[item],item) for item, total in totals.items() if simSums[item]!=0]
    rankings.sort()
    rankings.reverse()
#    print("Rankings:",rankings)
    mov = [r[1] for r in rankings]
    rankObject = {"recMovies":rankings}
    return mov

app=Flask(__name__)
cors=CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
'''
def hi():
    x="hey I am here!"
    return x
'''
@app.route("/submitreview", methods=["GET","POST"])

def submitReview():
#    y=hi()
    ratingObj={}
    try:
        if request.method == "POST":
            req_data=request.get_json()
#            print(json.dumps(req_data))
#            return json.dumps(req_data)
#            print((dumps(req_data)))
            d=dumps(req_data)
            l=json.loads(d)
#            print(l)
            ratingData = l
            nkName = ratingData['nickname'].replace('.','_')
            persistingData = { ratingData['id']:ratingData['rating'] }
            data=collection.find_one()
#            print("ID::",data['_id'])
            existingCollection = json.loads(dumps(data))
#            print("Existing Data:",existingCollection);
            if nkName in existingCollection:
                existingData = existingCollection[nkName]
                existingData[str(ratingData['id'])] = ratingData['rating']
            else:
                print('Here')
                existingData = {}
                existingData[str(ratingData['id'])] = ratingData['rating']
#            print("existingCollection:",persistingData)
            db.ratings.update_one({'_id': data['_id']},{'$set': {nkName:existingData}},upsert=True)
            return d

    except Exception as e:
        print(e)
    return "Default"

@app.route("/recommendMovies", methods=["GET","POST"])

def rMovies():
    try:
        if request.method == "POST":
            req_data = request.get_json()
            d = dumps(req_data)
            l = json.loads(d)
            recommendRequest = l
            nkName = recommendRequest['nickname'].replace('.','_')
            print(nkName)
            data=collection.find_one()
            mData = data
            mData.pop('_id',None)
            print(mData)
            rec = (getRecommendations(mData,nkName))
            print("REC:",dumps(rec))
        return dumps(rec)
    except Exception as e:
        print(e)
    return "Default"

@app.route("/getRatedMovies", methods=["GET"])

def getRmovies():
    try:
        if request.method == "GET":
            print("HERE::")
            param = request.args.get("person")
            nick = param.replace('.','_')
            data=collection.find_one()
            if nick in data:      
                return  dumps(data[nick])
            else:
                retObj = {"norecords": 1}
                return dumps(retObj)
    except Exception as e:
        print(e)
    return "Default"

@app.route("/searchMovie", methods=["GET"])

def getSearchMovie():
    try:
        if request.method == "GET":
            param = request.args.get("query")
            URL="https://api.themoviedb.org/3/search/movie?api_key=98c3f8bd00e0a1138dccdc4dc8a7d1b9&language=en-US&query="+param+"&page=1&include_adult=false"
            resp = requests.get(url=URL)
            return dumps(resp.json())
    except Exception as e:
        print(e)
    return ""
if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=6205)
