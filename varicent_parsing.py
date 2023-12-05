#!/usr/bin/env python

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

url = "https://www.varicent.com/blog"

# Define categories and their corresponding keywords
categories_keywords = {
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
                 "business policy", "organizational strategy"],
    "Other": []  # Any keywords not included in the above categories
}


def preprocess_text(text_vericent):
    text_vericent = text_vericent.lower()
    text_vericent = re.sub(r'[^\w\s]', '', text_vericent)
    words = word_tokenize(text_vericent)  # Tokenize text into words
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]  # Lemmatize words
    return lemmatized_words


def categorize_article(article_text):
    words = preprocess_text(article_text)
    for category, keywords in categories_keywords.items():
        for keyword in keywords:
            if keyword.lower() in words:
                return category
    return "Uncategorized"


try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with class 'post-content', 'post-title', and 'blog-post-author'
    article_texts = soup.find_all('div', class_='post-content')
    article_titles = soup.find_all('h3', class_='post-title')
    authors = soup.find_all('a', class_='blog-post-author')

    # Create a SQLite database connection and cursor
    conn = sqlite3.connect('databases/vericent_parsed_articles.sqlite')
    cursor = conn.cursor()

    # Create a table to store articles if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Articles (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Author TEXT,
            ArticleText TEXT,
            Category TEXT
        )
    ''')

    if article_titles and article_texts and authors:
        data = []
        # Extract titles, texts, authors, and categories and store them in the database
        for title, text, author in zip(article_titles[:5], article_texts[:5], authors[:5]):  # Limit to 5 articles
            title_text = title.text.strip()

            # Extract complete HTML content of the article
            article_response = requests.get(title.find('a')['href'])
            article_soup = BeautifulSoup(article_response.content, 'html.parser')

            # Extract only the visible text and remove unnecessary HTML elements
            visible_text = article_soup.find('span', {'id': 'hs_cos_wrapper_post_body'}).get_text(separator=' ',
                                                                                                  strip=True)

            text_text = visible_text  # Use the cleaned visible text
            author_text = author.text.strip()
            category = categorize_article(text_text)

            # Insert the data into the database
            cursor.execute('''
                INSERT INTO Articles (Title, Author, ArticleText, Category) VALUES (?, ?, ?, ?)
            ''', (title_text, author_text, text_text, category))

            # Append the fetched data to a list
            data.append([title_text, author_text, text_text, category])

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        # Convert the fetched data into a Pandas DataFrame
        df = pd.DataFrame(data, columns=['Title', 'Author', 'ArticleText', 'Category'])

        # Display the data in table format
        print(df)

        print("\n Data stored in the database successfully.")

    else:
        print("No article titles, texts, or authors found.")

except requests.RequestException as e:
    print(f"Request error: {e}")

except sqlite3.Error as sqle:
    print(f"SQLite error: {sqle}")

except Exception as ex:
    print(f"Error: {ex}")

# Connect to the SQLite database file
conn = sqlite3.connect('databases/vericent_parsed_articles.sqlite')

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
