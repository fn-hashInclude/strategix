from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import nltk
from nltk.corpus import stopwords
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")



# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('punkt_tab')
# nltk.download('stopwords')


from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from textblob import TextBlob
from textblob import TextBlob

# try:
#     nltk.download('punkt')
# except Exception as e:
#     print(f"Error downloading nltk resources: {e}")

app = Flask(__name__)

def generate_content_with_chatgpt(business_idea, scraped_contents):
    prompt = (
        f"You are an AI content generator. Based on the following competitor content, "
        f"generate a unique content piece that promotes the business idea '{business_idea}'.\n\n"
        f"Competitor Content:\n{scraped_contents}\n\n"
        f"Generated Content:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        return "Error: You have exceeded your API quota. Please try again later."
    except Exception as e:
        return f"Error generating content: {str(e)}"

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment

def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words and len(token) > 2]
    
    fdist = FreqDist(filtered_tokens)
    keywords = fdist.most_common(10)  
    return keywords

def scrape_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')

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
        url = url.strip() 
        if not url.startswith("http"):  
            url = "http://" + url
        scraped_content = scrape_content(url)
        scraped_contents.append(scraped_content)

    combined_content = " ".join(scraped_contents)
    print("Combined Content:", combined_content)

    if not combined_content.strip():
        return render_template('index.html', error="No valid content scraped. Please check the URLs.")

    generated_content = generate_content_with_chatgpt(business_idea, combined_content)

    keywords = extract_keywords(combined_content)
    sentiment = analyze_sentiment(combined_content)

    return render_template('index.html', generated_content=generated_content, scraped_contents=combined_content, keywords=keywords, sentiment=sentiment)


if __name__ == '_main_':
    app.run(debug=True)