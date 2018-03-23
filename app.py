# -*- coding: utf-8 -*- 
from flask import Flask, render_template, json, request, jsonify
from MethodsForTweet import *
import json 
from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob

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
    filex.write("===========================" +'\n')
    filex.write(key['text'].encode('utf-8')+'\n' )
  filex.close()
  return "bien", 200

@app.route('/txt')
def bayes():
  train = [
    ('Extraordinaria reunion Al Gore y AMLO , me dio un gusto enorme conocer sus profundas coincidencias sobre Accion Climatica', 'pos'),
    ('AMLO fue el unico que estuvo a la altura.', 'pos'),
    ('AMLO a sabido ganarse nuestra confianza y por eso ahora somos muchos los que lo apoyamos. ', 'pos'),
    ('No hay otra mejor opcion en Mexico que AMLO. Los demas partidos han demostrado que trabajan para su bolsillo ', 'pos'),
    ('Al final queda la imagen de un AMLO prudente, inteligente ', 'pos'),
    ('VOTO MASIVO POR  AMLO  aun que les arda ', 'pos'),
    ('Arriba papa AMLO ', 'pos'),
    ('prometio trabajar junto con algore para hacer frente al cambio climatico', 'pos'),
    ('Hasta Mitofsky senala que AMLO continua creciendo, Anaya y Meade van a la baja', 'pos'),
    ('Segun El Financiero, AMLO continua siendo el preferido', 'pos'),
    ('convence a mas mexicanos y despega 4 puntos arriba en las encuestas. Inalcanzable', 'pos'),
    ('Lopitos,somos 70% de Mexicanos q no te creemos.Enganas a medio mundo.Tienes genes de dictador despistado.', 'neg'),
    ('Las contradicciones de AMLO', 'neg'),
    ('Refuta Penia a AMLO; defiende reforma energetica', 'neg'),
    ('hablan mucho de Suecia y Noriega... pero quieren votar por el que le mira hacia Venezuela', 'neg'),
    ('las propuestas de AMLO me dan pesadillas', 'pos'),
    ('El video viral que muestra la ignorancia de AMLO esta manipulado', 'neg')
  ]
  cl = NaiveBayesClassifier(train)
  print(cl.classify("Las propuestas de AMLO parecieron razonables y viables"))


  return "OK", 200


if __name__ == "__main__":
    app.run(port=5000)
