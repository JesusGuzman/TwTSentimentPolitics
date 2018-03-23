from flask import Flask, render_template, json, request, jsonify
from MethodsForTweet import *
import json 

app = Flask(__name__)
twitter_api = oauth_login()

@app.route('/')
def main():
  return "OK", 200

@app.route('/amlo')
def amlo():
  entrada =1;
  if entrada == 1 :
    word = "amlo"
  elif entrada == 2 :
    word = "anaya"
  else :
    word = "meade"
  results = twitter_search(twitter_api, word, max_results= 1 )
  filex = open('test.txt','w')
  for key in results:
    filex.write(key['text'].encode('utf-8'))
  filex.close()
  return "bien", 200

@app.route('/analisys')
def bayes():
  return "OK", 200


if __name__ == "__main__":
    app.run(port=5000)
