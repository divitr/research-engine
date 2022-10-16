from transformers import BertTokenizerFast, EncoderDecoderModel
from newspaper import Article
from bs4 import BeautifulSoup
from keybert import KeyBERT
from flask import Flask, render_template, request, json, send_from_directory
from flask_cors import CORS, cross_origin
import random
import time
import re
import requests
import torch
import bs4
from googlesearch import search
from mechanize import Browser
import json


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



#defines tokenizer, summarization model, and keyphrase extraction model
def init():
    global device
    global tokenizer
    global model
    global kw_model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizerFast.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
    model = EncoderDecoderModel.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(device)
    kw_model = KeyBERT()

#extracts body text from url
def get_text(url):
  article = Article(url)
  article.download()
  try:
    article.parse()
  except:
    pass
  page_text = article.text
  len_page_text = len(re.findall(r'\w+', page_text))
  if page_text == "" or len_page_text <= 100:
    try: 
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all(['h1', 'p'])
        text = [result.text for result in results]
        if len(re.findall(r'\w+', ' '.join(text))) <= 100:
            pass
        else:
            return(' '.join(text))
    except:
      pass

  elif page_text == "Bad Message 400":
    pass
  else:
    return article.text
  return None

#returns three parallel lists (len <= 10):
#.  urls - list of urls
#.  titles - list of titles of webpages
#.  texts - list of body text of webpages
def get_search_results(searchTerm):
  urls = []
  for url in search(searchTerm,num_results=20):
    urls.append(url)
  final_urls = []
  titles = []
  texts = []
  obj = []
  for i in range(len(urls)):
    url = urls[i]
    br = Browser()
    try:
      res = br.open(url)
    except:
      continue
    data = res.get_data() 

    soup = BeautifulSoup(data, 'html.parser')
    title = soup.find('title')
    if title is None:
      continue

    text = get_text(url)
    if text is None:
      continue

    data = {"url": url, "title": title.renderContents().decode("utf-8"), "text": text}
    obj.append(data)
    # titles.append(title.renderContents().decode("utf-8"))
    # final_urls.append(url)
    # texts.append(text)
  return obj
#generates summary of text
def generate_summary(text):
  inputs = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
  input_ids = inputs.input_ids.to(device)
  attention_mask = inputs.attention_mask.to(device)

  output = model.generate(input_ids, attention_mask=attention_mask,max_new_tokens=200)

  st = tokenizer.decode(output[0], skip_special_tokens=True)

  return '. '.join(list(map(lambda x: x.strip().capitalize(), st.split('.'))))

#generate_summary function wrapper
def summarize(chunks):
  tot_summary = str()
  for chunk in chunks:
    summary = generate_summary(chunk)
    tot_summary = tot_summary + summary
  return tot_summary

#chunks text so that it fits NLP bounds
def chunker(text):
  max_chunk = 500
  pages = []

  sentences = text.split('<eos>')
  current_chunk = 0 
  chunks = []

  for sentence in sentences:
      if len(chunks) == current_chunk + 1: 
          if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
              chunks[current_chunk].extend(sentence.split(' '))
          else:
              current_chunk += 1
              chunks.append(sentence.split(' '))
      else:
          chunks.append(sentence.split(' '))

  for chunk_id in range(len(chunks)):
      chunks[chunk_id] = ' '.join(chunks[chunk_id])

  return chunks

#returns 3 keyphrases from text (2 words or less)
def keywords(text):
  keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=3, use_mmr=True)
  final_keywords = [keyword[0] for keyword in keywords]
  return final_keywords

#generates dictionary
def generate_dict(url,title,summary,keyphrases):
  d = {'url' : url,
       'title' : title,
       'summary' : summary,
       'keyphrases' : keyphrases}
  return d

#generates summary and extracts keyphrases, returns dictionary
def process_url(url,title,text):
  chunks = chunker(text)
  summary = summarize(chunks)
  keyphrases = keywords(text)
  dic = generate_dict(url,title,summary,keyphrases)
  return dic

def main(query):
  urls,titles,texts = get_search_results(query)
  dict_list = []
  for i in range(len(urls)):
    if len(dict_list) == 10:
      break
    url = urls[i]
    title = titles[i]
    text = texts[i]
    dic = process_url(url,title,text)
    if dic is not None:
      dict_list.append(dic)

  mlti_text = ''
  for dic in dict_list:
    mlti_text += dic['summary']

  chunks = chunker(mlti_text)
  mlti_summary = summarize(chunks)
  dict_list.append({'multidoc summary' : mlti_summary})

@app.route('/')
def base():
  return send_from_directory('client/dist', 'index.html')

@app.route("/<path:path>")
def home(path):
  return send_from_directory('client/dist', path)

@app.route('/info/<query>')
def getURLS(query):
    return app.response_class(response=json.dumps(get_search_results(query)), mimetype='application/json')


"""
schema:
{
    "url": <url>,
    "title": <title>,
    "text": <text>,
}
"""
@app.route('/summarize', methods=['POST'])
def summarizeURL():
    contentType = request.headers.get('Content-Type')
    if contentType == 'application/json':
        init()
        query = request.json
        dic = process_url(query["url"], query["title"], query["text"])
        return app.response_class(response=json.dumps(dic), mimetype='application/json')
    else:
        return '<h5>Set content type to application/json</h5>'
        

data = [{
		"url": "https://dogwoof.com/tdog",
		"title": "TDog — Dogwoof Documentaries",
		"text": "TDog is Dogwoof’s by-invitation-only production fund. The fund launched in 2016 in order to support the making of quality documentaries across the world.\n\nWestwood: Punk, Icon, Activist was one of our first TDog features and made its World Premiere in Sundance 2018, this year we premiered Halston by Frédéric Tcheng (Dior and I), again in Sundance. Currently we have six more projects in production, including a documentary series.\n\nBesides financing, Dogwoof is increasingly directly producing projects and co-producing others. The objective is to fund and produce 6-10 projects a year, half doc-series and half feature docs. Dogwoof's TDog is also involved in fiction remakes of their unscripted projects."
	},{
		"url": "https://dogwoof.com/tdog",
		"title": "TDog — Dogwoof Documentaries",
		"text": "TDog is Dogwoof’s by-invitation-only production fund. The fund launched in 2016 in order to support the making of quality documentaries across the world.\n\nWestwood: Punk, Icon, Activist was one of our first TDog features and made its World Premiere in Sundance 2018, this year we premiered Halston by Frédéric Tcheng (Dior and I), again in Sundance. Currently we have six more projects in production, including a documentary series.\n\nBesides financing, Dogwoof is increasingly directly producing projects and co-producing others. The objective is to fund and produce 6-10 projects a year, half doc-series and half feature docs. Dogwoof's TDog is also involved in fiction remakes of their unscripted projects."
	},]

@app.route('/testinfo')
def test():
    return app.response_class(response=json.dumps(data), mimetype='application/json')

dataa = {
	"url": "https://dogwoof.com/tdog",
	"title": "TDog — Dogwoof Documentaries",
	"summary": "Tdog is dogwoof ’ s by - invitation - only production fund. Currently we have six more projects in production, including a documentary series. The objective is to fund and produce 6 - 10 projects a year, half doc - series and half feature docs. Tdog's tdog also involved in fiction remakes of their unscripted projects. ",
	"keyphrases": [
		"dogwoof tdog",
		"premiere sundance",
		"fiction remakes"
	]
}

@app.route('/testsummary', methods=['POST'])
def summ():
    return app.response_class(response=json.dumps(dataa), mimetype='application/json')

app.run()