from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import sql
from Category_URL import Category_List

app = Flask(__name__)

def scrape_books():
  
    try:
        books = []
        base_url = "http://books.toscrape.com/catalogue/category/books/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        # Loop through each category in the category list
        for category_url in Category_List:
            url = base_url + category_url
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract genre from the category listing page
            genre = extract_genre(soup)
            # Extract book data from the current page
            books.extend(extract_book_data(soup, genre))

            # Follow the next page link if available
            next_page = soup.select_one('li.next > a')
            while next_page:
                next_page_url = next_page['href']
                next_url = requests.compat.urljoin(url, next_page_url)
                response = requests.get(next_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract book data from the next page
                books.extend(extract_book_data(soup, genre))
                next_page = soup.select_one('li.next > a')

        return books

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def extract_genre(soup):
    genre_element = soup.select_one('div.page-header > h1')
    return genre_element.text.strip() if genre_element else None

def extract_book_data(soup, genre):
    
    book_data = []
    for book in soup.find_all(class_="product_pod"):
        try:
            title = book.h3.a["title"]
            price = book.find(class_="price_color").text.strip()
            instock = book.find('p', class_="instock availability").text.strip()
            rating_element = book.select_one('p.star-rating')
            rating = rating_element['class'][1].lower() if rating_element else None
            book_data.append({"title": title, "price": price, "instock": instock, "rating": rating, "genre": genre})
        except (AttributeError, IndexError) as e:
            print(f"Error parsing book data: {e}")
            continue
    return book_data

def insert_books_into_database(books, db_user, db_password):
    """
    Insert the list of books into the database, creating tables as needed.
    """
    print("Connecting to the database...")

    # Hardcoded database host and name
    db_host = "localhost"
    db_name = "postgres"
    
    connection_url = f"host={db_host} dbname={db_name} user={db_user} password={db_password}"
    
    try:
        with psycopg2.connect(connection_url) as conn:
            print("Connected to the database successfully.")
            with conn.cursor() as cursor:
                # Extract unique genres from books
                genres = set(book['genre'] for book in books)

                # Loop through each genre and create table if not exists
                for genre in genres:
                    table_name = genre.replace(" ", "_").lower()
                    create_table_if_not_exists(cursor, table_name)

                    print(f"Inserting books into the {table_name} table...")
                    # Insert each book into the corresponding genre table
                    for book in [b for b in books if b['genre'] == genre]:
                        try:
                            savepoint = "savepoint_" + book['title'].replace(" ", "_").replace("'", "")
                            cursor.execute(sql.SQL("SAVEPOINT {}").format(sql.Identifier(savepoint)))
                            cursor.execute(
                                sql.SQL("INSERT INTO {} (title, price, instock, rating) VALUES (%s, %s, %s, %s)").format(sql.Identifier(table_name)),
                                (book['title'], book['price'], book['instock'], book['rating'])
                            )
                        except psycopg2.errors.UniqueViolation:
                            print(f"Book '{book['title']}' already exists in the {table_name} table. Skipping...")
                            cursor.execute(sql.SQL("ROLLBACK TO SAVEPOINT {}").format(sql.Identifier(savepoint)))
                            continue
                    print(f"{len([b for b in books if b['genre'] == genre])} books inserted successfully.")

            conn.commit()  # Commit all changes at once
    except Exception as e:
        print(f"Error occurred during database transaction: {e}")
    finally:
        print("Connection to the database closed.")

def create_table_if_not_exists(cursor, table_name):
    """
    Create a table for a specific genre if it does not already exist.
    """
    print(f"Creating table {table_name} if not exists...")
    cursor.execute(
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY, 
                title VARCHAR UNIQUE, 
                price VARCHAR, 
                instock VARCHAR, 
                rating VARCHAR
            )
        """).format(sql.Identifier(table_name))
    )
    print(f"Table {table_name} created.")

@app.route("/books")
def get_books():
    """
    Flask route to scrape books and insert them into the database.
    """
    # Prompt the user to input the database username and password
    db_user = input("Enter your database username: ")
    db_password = input("Enter your database password: ")

    all_books = scrape_books()
    if all_books:
        insert_books_into_database(all_books, db_user, db_password)
        return jsonify(all_books)
    else:
        return jsonify({"error": "Failed to scrape books."}), 500

if __name__ == "__main__":
    app.run(debug=True)