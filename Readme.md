A script to scrape business research articles from provided web pages, categorize the articles based on predefined 
rules, and store the information in a database.

1. Web Scraping:
A Python script using libraries requests and BeautifulSoup to scrape 5 latest (by the publication date) articles from 
each one of the provided URLs:
- https://www.varicent.com/blog
- https://www.everstage.com/blog
2. Extract the following details: title, author(s), publication date, and the article text.
3. Script dynamically identifying the latest articles at the time of execution.
4. Data Categorization:
Implement a simple categorization function within the script that assigns a category to each article based on the 
presence of specific keywords within the article text.
Categories and corresponding keywords will be provided below (e.g., "Finance" for articles with the keywords 
"economics," "stock market," etc.).
5. Database Integration:
- SQLite was used for creating a database and store the scraped data.
- The database contains a single table with columns for title, author(s), publication date, article text, and category.


To set up and run the script, open the specified files in the IDE 
(PyCharm, Jupyter Notebook, Google Colab or other) and install the necessary software, 
packages and libraries before launching.

- python 3.10
- conda latest version
- requests == 2.31.0
- bs4 == 4.12.2
- pandas == 2.1.1
- nltk == 3.8.1

Files with src code: 
- everstage_parsing.py
- varicent_parsing.py

