# Book-Scraper
This project is a Python web scraper that extracts book data from the website "http://books.toscrape.com". The scraped data includes the book title, price, availability, rating, and genre. The scraped data is then inserted into a PostgreSQL database, with separate tables created for each genre.


Dependencies

The following Python libraries are required to run this project:

    Flask
    requests
    beautifulsoup4
    psycopg2

You can install these dependencies using pip:


pip install flask requests beautifulsoup4 psycopg2


Project Structure

The project consists of the following files:

    main.py: The main Python script that contains the web scraper and Flask application.
    Category_URL.py: A Python file containing a list of category URLs for the website.

#Code Explanation

main.py

#Imports

The script imports the required libraries: Flask, requests, BeautifulSoup, and psycopg2.

# scrape_books Function

    This function scrapes book data from the website.
    It starts with the base URL for the "Books" category and loops through the list of category URLs from Category_URL.py.
    For each category URL, it sends a GET request to the website and parses the HTML content using BeautifulSoup.
    The function extracts the genre information from the category listing page.
    It then extracts book data (title, price, availability, rating) from individual book pages within the category.
    If there are multiple pages for a category, the function follows the "Next" links to scrape data from all pages.
    The scraped book data is stored in a list of dictionaries, with each dictionary representing a book.
    The function handles exceptions that may occur during the scraping process.

# extract_book_data Function

    This is a helper function that extracts book data from individual book pages.
    It takes the BeautifulSoup object and the genre as input.
    It loops through the book elements on the page and extracts the book data (title, price, availability, rating).
    The extracted book data is appended to a list, which is returned by the function.

# insert_books_into_database Function

    This function is responsible for inserting the scraped book data into a PostgreSQL database.
    It creates separate tables for each genre if they don't already exist.
    It then inserts the book data into the corresponding genre table, handling any unique constraint violations.
    This function uses user input for database credentials for security purposes.

# Flask Routes

    The /books route calls the scrape_books function to scrape book data from all categories.
    If the scraping is successful, it calls the insert_books_into_database function to insert the scraped data into the database.
    The scraped book data is returned as a JSON response.
    If the scraping fails, an error message is returned as a JSON response.

# Main Function

    The script runs the Flask application in debug mode when executed directly.

# Usage

    Make sure you have installed the required dependencies.
    Create a PostgreSQL database.
    Run the main.py script.
    You will be prompted to enter your database username and password.
    Visit http://localhost:5000/books in your web browser to trigger the scraping process and insert the scraped data into the database.

Note: This implementation assumes that the website's HTML structure and URL patterns remain consistent across all categories and subcategories. If there are any deviations, you may need to adjust the code accordingly.
