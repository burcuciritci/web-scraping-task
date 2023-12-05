import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from pymongo import MongoClient
from collections import Counter
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging


def fetch_and_store_data_to_mongodb(base_url, page_count, database_name):
    global client
    try:
        # MongoDB URI and database name
        mongo_uri = "mongodb://localhost:27017"
        client = MongoClient(mongo_uri)
        db = client[database_name]

        # Configure the log file
        log_directory = "logs"
        log_file_path = os.path.join(log_directory, "logs.log")
        os.makedirs(log_directory, exist_ok=True)
        logging.basicConfig(filename=log_file_path, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        stats_data = {
            "elapsed_time": 0,
            "count": 0,
            "date": "",
            "success_count": 0,
            "fail_count": 0
        }

        start_time = datetime.now()

        all_text_list = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Use executor.map to parallelize fetching
            futures = [executor.submit(fetch_page, base_url, page_number, db, stats_data) for page_number in range(1, page_count + 1)]

            for future in futures:
                page_data = future.result()
                if page_data:
                    url, page_content = page_data
                    all_text_list.append(page_content)
                    logging.info(f"Fetching page content. URL: {url}")

        all_text = ' '.join(all_text_list)

        # Create a Counter to count words
        word_counter = Counter(all_text.split())

        # Get the top 10 most common words
        top_10_words = word_counter.most_common(10)

        word_frequency_data = [{"word": word, "count": count} for word, count in top_10_words]
        db.word_frequency.insert_one({"top_10_words": word_frequency_data})

        # Create a chart
        words, counts = zip(*top_10_words)
        plt.bar(words, counts)
        plt.xlabel('Words')
        plt.ylabel('Count')
        plt.title('Top 10 Most Frequently Used Words')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('top_10_most_frequently_used_words.png')
        plt.show()

        # Log: Write process time and statistics information to the log file
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        stats_data["elapsed_time"] = elapsed_time.total_seconds()
        stats_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        logging.info(f"Data retrieval process completed. Elapsed time: {elapsed_time}")
        logging.info(f"Statistics Information: {stats_data}")

        db.stats.insert_one(stats_data)

        # Close the MongoDB connection
        client.close()

    except Exception as e:

        print(f"An error occurred: {e}")

    finally:
        if 'client' in locals() and client:
            client.close()


def fetch_page(base_url, page_number, db, stats_data):
    url = f"{base_url}page/{page_number}/"
    logging.info(f"Fetching page {page_number}. URL: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        stats_data["count"] += 1
        soup = BeautifulSoup(response.text, 'html.parser')
        parent_element = soup.find('div', class_='kategori_yazilist')
        news_titles = parent_element.select('.post-link')

        for news in news_titles:
            news_url = news['href']
            logging.info(f"Fetching news content. URL: {news_url}")

            # Make a new request to fetch news details
            news_response = requests.get(news_url)

            if news_response.status_code == 200:
                news_soup = BeautifulSoup(news_response.text, 'html.parser')
                content = news_soup.select_one('.yazi_icerik')

                # Insert data into the 'news' collection
                news_data = {
                    "url": news_url,
                    "header": news_soup.select_one('.single_title').text if news_soup.select_one(
                        '.single_title') else "",
                    "summary": news_soup.select_one('.single_excerpt').text if news_soup.select_one(
                        '.single_excerpt') else "",
                    "text": content.text,
                    "img_url_list": [img_element['src'] for img_element in
                                     news_soup.select('.yazi_icerik img')] if news_soup.select(
                        '.yazi_icerik img') else [],
                    "publish_date": "",
                    "update_date": ""
                }
                db.news.insert_one(news_data)
                stats_data["success_count"] += 1
                return news_url, content.text
    stats_data["fail_count"] += 1
    return None


def print_grouped_data_by_update_date(db_name, collection_name):
    global client
    try:
        # MongoDB URI
        mongo_uri = "mongodb://localhost:27017"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)

        # Select the database
        db = client[db_name]

        # Select the collection
        collection = db[collection_name]
        print(collection.index_information())

        # Check if the 'update_date' field exists in the collection
        if db[collection_name].count_documents({"update_date": {"$exists": True}}) == 0:
            raise Exception("'update_date' field does not exist in the collection.")

        # Group the data by the 'update_date' field and print each group
        grouped_data = collection.aggregate([
            {"$group": {"_id": "$update_date", "data": {"$push": "$$ROOT"}}}
        ])

        for group in grouped_data:
            update_date = group["_id"]
            data = group["data"]

            print(f"\nUpdate Date: {update_date}\n")
            for item in data:
                print(item)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the MongoDB connection
        if 'client' in locals() and client:
            client.close()


print(fetch_and_store_data_to_mongodb('https://turkishnetworktimes.com/kategori/gundem/', 50, 'burcu_ozturk'))
#print_grouped_data_by_update_date("burcu_ozturk", "news")
