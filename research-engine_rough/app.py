from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration
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

app = Flask(__name__)
#defining summarization model and keyphrase detection model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = BertTokenizerFast.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
model = EncoderDecoderModel.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(device)
kw_model = KeyBERT()


@app.route('/', methods=['GET','POST'])
def search():
    resultsVisible = False;
    searchTerm="";
    searchResults={}

    if request.method == "POST":
        searchTerm =  request.form['searchTerm'];
        resultsVisible = True;
        searchResults = getSearchResults(searchTerm)
    return render_template('search.html'
                            ,searchTerm=searchTerm
                            ,resultsVisible=resultsVisible
                            ,searchResultLen = len(searchResults)
                            ,searchResultURLs=list(searchResults.keys())
                            ,searchResultSummaries=list(searchResults.values()))

@app.route('/summarize', methods=['POST', 'GET'])
def summarize():
    if request.method == 'POST':
        #user = request.form['nm']
        url = request.get_data().decode();
        #return redirect(url_for('success', name=user))
    else:
        #user = request.args.get('nm')
        url = request.args.get('url')
        #return redirect(url_for('success', name=user))
    # now that we have url, get data, summarize and send results back
    #time.sleep(random.randint(0,9))

    #return ("SUMMARY FOR " + str(url));
    return processURL(str(url));

def init():
    global device
    global tokenizer
    global model
    global kw_model
    #defining summarization model and keyphrase detection model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizerFast.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
    model = EncoderDecoderModel.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(device)
    kw_model = KeyBERT()

def getSearchResults(searchTerm):
    searchResults={}
    
    urls = ["https://towardsdatascience.com/a-bayesian-take-on-model-regularization-9356116b6457",
            "https://medium.com/personal-growth/how-soulmates-and-love-at-first-sight-let-us-down-9e0fb993cdf8",
            "https://hackernoon.com/will-the-game-stop-with-gamestop-or-is-this-just-the-beginning-2j1x32aa",
            "http://fox13now.com/2013/12/30/new-year-new-laws-obamacare-pot-guns-and-drones/",
            "https://www.bbc.com/news/business-62144776",
            "https://www.forbes.com/sites/davidaxe/2022/07/12/ukraine-liberated-snake-island-now-ukrainian-grain-is-about-to-flow/?sh=219d3db74323",
            "https://www.nature.com/articles/d41586-022-01906-6",
            "https://www.britannica.com/science/nuclear-fission",
            "https://bio.libretexts.org/Bookshelves/Human_Biology/Book%3A_Human_Biology_(Wakim_and_Grewal)/05%3A_Cells/5.07%3A_Cell_Transport",
            "https://www.science.org/content/article/beyond-silicon-15-billion-us-program-aims-spur-new-types-computer-chips"]
            
    #for x in range(10):
    #    searchResults["http://example.com/" + searchTerm + "---" + str(x)]=""

    for x in range(len(urls)):
        searchResults[urls[x]]=""

    #searchResults[urls[0]]=""
    
    return searchResults


#returns body of text from website
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

#preprocesses text
def preprocess(text):
  if not text:
    text=""
  text = text.replace('.', ".<eos>")
  text = text.replace('?', "?<eos>")
  text = text.replace('!', "!<eos>")
  return text

def generate_summary(text):
  inputs = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
  input_ids = inputs.input_ids.to(device)
  attention_mask = inputs.attention_mask.to(device)

  output = model.generate(input_ids, attention_mask=attention_mask)

  return tokenizer.decode(output[0], skip_special_tokens=True)

#summarizes chunks of text
def summarize(chunks):
  tot_summary = str()
  for chunk in chunks:
    summary = generate_summary(chunk)
    tot_summary = tot_summary + summary
  return tot_summary

#extracts key phrases
def keywords(text):
  keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=3, use_mmr=True)
  final_keywords = [keyword[0] for keyword in keywords]
  return final_keywords

#breaks down text into chunks for the NLP
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



def processURL(url):
  text = get_text(url)
  processed_text = preprocess(text)
  chunks = chunker(processed_text)
  summary = summarize(chunks)
  #keyphrases = keywords(text)
  return summary;

if __name__=="__main__":
    from waitress import serve
    app.run(debug=True)
    #serve(app, host="0.0.0.0", port=8080)