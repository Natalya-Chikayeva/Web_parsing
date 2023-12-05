#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# URLs to scrape
urls = [
    "https://www.everstage.com/blog"
]

# Define categories and their corresponding keywords
categories = {
    "Finance": ["economics", "stock market", "financial management", "investment", "capital", "fiscal policy"],
    "Marketing": ["marketing strategy", "consumer behavior", "branding", "advertising", "market research",
                  "digital marketing"],
    "Human Resources (HR)": ["recruitment", "talent management", "organizational culture", "employee engagement",
                             "workforce planning", "diversity and inclusion"],
    "Operations Management": ["supply chain", "logistics", "production", "quality control", "inventory management",
                              "operational efficiency"],
    "Information Technology (IT)": ["information systems", "cybersecurity", "data analytics", "software development",
                                    "cloud computing", "IT infrastructure"],
    "Entrepreneurship": ["start-up", "venture capital", "innovation", "business model", "scaling business",
                         "entrepreneurial finance"],
    "Strategy": ["competitive strategy", "business planning", "strategic management", "corporate governance",
                 "business policy", "organizational strategy"]
    # 'Other' category will handle any keywords not included above
}


# Function to lemmatize text
def perform_lemmatization(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())  # Tokenize text into words
    lemmatized_words = [lemmatizer.lemmatize(word) for word in tokens]  # Lemmatize words
    return ' '.join(lemmatized_words)


# Function to categorize articles based on lemmatized keywords
def categorize_article(article_text):
    lemmatized_text = perform_lemmatization(article_text)
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in lemmatized_text:
                return category
    return "Other"  # Default category if no match found


# Function to scrape article details including links, authors, and text
def scrape_articles(url_everstage):
    response = requests.get(url_everstage)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('a', {'class': 'blog-title-link'})[:5]  # Limit to the first 5 articles

        article_data = []
        base_url = 'https://www.everstage.com'  # Base URL of the website
        for article in articles:
            title_elem = article.find('h2')
            if title_elem:
                link = base_url + article['href']

                # Visit the article page to extract more information
                article_response = requests.get(link)
                if article_response.status_code == 200:
                    article_content = article_response.content.decode('utf-8', 'ignore')
                    article_soup = BeautifulSoup(article_content, 'html.parser')

                    # Extracting title
                    title = title_elem.text.strip()

                    # Extracting author
                    author_elem = article_soup.find('a', {'class': 'author-link'})
                    if author_elem:
                        author = author_elem.find('div', {'class': 'author-name'}).text.strip()
                    else:
                        author = "Unknown"

                    # Extracting article text if the element exists
                    article_text_elem = article_soup.find('div', {'class': 'blog-rich-text'})
                    article_text = article_text_elem.text.strip() if article_text_elem else ""

                    # Categorize the article
                    category = categorize_article(article_text)

                    # Append the data to the article_data list along with the category
                    article_data.append({'Title': title, 'Link': link, 'Author': author, 'Text': article_text,
                                         'Category': category})

        return article_data
    else:
        print(f"Failed to fetch data from {url_everstage}")
        return None


# Scraping data from each URL
all_articles_data = []
for url in urls:
    articles_data = scrape_articles(url)
    if articles_data:
        all_articles_data.extend(articles_data)

# Creating a DataFrame from the scraped data
articles_df = pd.DataFrame(all_articles_data)
print(articles_df)

# Storing data into an SQLite database
conn = sqlite3.connect('databases/everstage_scraped_articles.sqlite')
articles_df.to_sql('articles', conn, if_exists='replace', index=False)

# Committing changes and closing the connection
conn.commit()
conn.close()

# Connect to the SQLite database file
conn = sqlite3.connect('databases/everstage_scraped_articles.sqlite')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Fetch all records from the 'articles' table
print("Result from database for checking: ")
cursor.execute("SELECT * FROM articles")
all_rows = cursor.fetchall()
for row in all_rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
