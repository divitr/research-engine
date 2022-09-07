#!pip install bs4 -q
#!pip install newspaper3k -q
#!pip install googlesearch-python -q
#!pip install mechanize -q
#!pip install transformers -q
#!pip install keybert -q

from transformers import BertTokenizerFast, EncoderDecoderModel
from newspaper import Article
from bs4 import BeautifulSoup
from keybert import KeyBERT
from flask import Flask, render_template, request, json
import random
import time
import re
import requests
import torch
import bs4
from googlesearch import search
from mechanize import Browser
import json

def init():
    global device
    global tokenizer
    global model
    global kw_model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizerFast.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
    model = EncoderDecoderModel.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(device)
    kw_model = KeyBERT()

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

def get_search_results(searchTerm):
  urls = []
  for url in search(searchTerm,num_results=20):
    urls.append(url)
  final_urls = []
  titles = []
  texts = []
  for i in range(len(urls)):
    url = urls[i]
    br = Browser()
    try:
      res = br.open(url)
    except:
      continue
    data = res.get_data() 

    soup = BeautifulSoup(data)
    title = soup.find('title')
    if title is None:
      continue

    text = get_text(url)
    if text is None:
      continue
    
    titles.append(title.renderContents().decode("utf-8"))
    final_urls.append(url)
    texts.append(text)
  return final_urls,titles,texts

def generate_summary(text):
  inputs = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
  input_ids = inputs.input_ids.to(device)
  attention_mask = inputs.attention_mask.to(device)

  output = model.generate(input_ids, attention_mask=attention_mask,max_new_tokens=200)

  st = tokenizer.decode(output[0], skip_special_tokens=True)

  return '. '.join(list(map(lambda x: x.strip().capitalize(), st.split('.'))))

def summarize(chunks):
  tot_summary = str()
  for chunk in chunks:
    summary = generate_summary(chunk)
    tot_summary = tot_summary + summary
  return tot_summary

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

def keywords(text):
  keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=3, use_mmr=True)
  final_keywords = [keyword[0] for keyword in keywords]
  return final_keywords

def generate_dict(url,title,summary,keyphrases):
  d = {'url' : url,
       'title' : title,
       'summary' : summary,
       'keyphrases' : keyphrases}
  return d

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
  print(dict_list)
  
  output_file = json.dumps(dict_list, indent=4, separators=(", ", " : "))
  with open("output.json", "w") as outfile:
    outfile.write(output_file)

init()
main('top quark')
