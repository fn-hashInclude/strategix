from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import nltk

nltk.download('punkt')
nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from textblob import TextBlob
from textblob import TextBlob

try:
    nltk.download('punkt')
except Exception as e:
    print(f"Error downloading nltk resources: {e}")

app = Flask(__name__)

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment

def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    fdist = FreqDist(tokens)
    keywords = fdist.most_common(10)  
    return keywords

def scrape_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example: Scrape all paragraph texts
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_content():
    business_idea = request.form['business_idea']
    competitors = request.form.getlist('competitors')

    scraped_contents = []
    for url in competitors:
        scraped_content = scrape_content(url.strip())
        scraped_contents.append(scraped_content)

    combined_content = " ".join(scraped_contents)

    # Analyze content
    keywords = extract_keywords(combined_content)
    sentiment = analyze_sentiment(combined_content)

    # Placeholder for content generation logic
    generated_content = f"Generated content for {business_idea} based on competitor analysis."

    return render_template('index.html', generated_content=generated_content, scraped_contents=combined_content, keywords=keywords, sentiment=sentiment)



if __name__ == '_main_':
    app.run(debug=True)