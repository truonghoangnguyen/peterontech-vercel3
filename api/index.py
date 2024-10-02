# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return 'Hello, World!'

# @app.route('/about')
# def about():
#     return 'About'

import json
from urllib.parse import quote, urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_decoding_params(gn_art_id):
    response = requests.get(f"https://news.google.com/articles/{gn_art_id}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    div = soup.select_one("c-wiz > div")
    return {
        "signature": div.get("data-n-a-sg"),
        "timestamp": div.get("data-n-a-ts"),
        "gn_art_id": gn_art_id,
    }

def decode_urls(articles):
    articles_reqs = [
        [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{art["gn_art_id"]}",{art["timestamp"]},"{art["signature"]}"]',
        ]
        for art in articles
    ]
    payload = f"f.req={quote(json.dumps([articles_reqs]))}"
    headers = {"content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
    response = requests.post(
        url="https://news.google.com/_/DotsSplashUi/data/batchexecute",
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return [json.loads(res[2])[1] for res in json.loads(response.text.split("\n\n")[1])[:-2]]

@app.route('/url', methods=['GET'])
def get_original_url():
    
    encoded_url = request.args.get('url')
    # return encoded_url + 'Hello, World!'
    if not encoded_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        # Get the article ID from the URL
        gn_art_id = urlparse(encoded_url).path.split("/")[-1]
        
        # Get decoding parameters
        articles_params = [get_decoding_params(gn_art_id)]
        
        # Decode the URL
        decoded_urls = decode_urls(articles_params)
        
        return jsonify({"origin_url": decoded_urls[0]})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return 'Hello, World!'

# http://localhost:3001/url?url=https://news.google.com/rss/articles/CBMi0gFBVV95cUxOQ2RyNGtCSEFNN2NoQ0YwbDEweDRhQTRVbTlkYUJKZm9QMHdJeTRDMG5RTXNnQ09vOUtBbkpoQ1NGR3NQYmJNWkMwbDQ2N05yQS1yb1ZxenBOVGlCUzU2ZTQ3LWxCRWJGNllEYlJNTFZ0TXEydlNVS195b0VQY215OF9MeUMyUEhEc1p2cV9sRTE5QUZVZGs2WkVrOUFwYWhjc2p0bUowbnBvUzQycmpoMXFZSWgtZFNlYi1INnd0b0RSQzdVQWJUbnhNTVJVQ21xR3c?oc=5