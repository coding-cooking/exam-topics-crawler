import json
import pymongo
from pymongo import MongoClient
import time
from dotenv import load_dotenv
import os

load_dotenv()
def bulk_insert_to_mongodb(json_file, mongodb_uri, database_name, collection_name):
    # Start timing
    start_time = time.time()

    # Connect to MongoDB
    try:
        # Create a MongoDB client
        client = MongoClient(mongodb_uri)

        # Select the database and collection
        db = client[database_name]
        collection = db[collection_name]

        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Prepare bulk write operations
        bulk_operations = []

        # Process each item in the data
        for item in data:
            # Prepare the document according to the schema
            document = {
                'topicId': item['topic_id'],
                'question': {
                    'questionContent': item['question']['questionContent'],
                    'questionImage': item['question'].get('questionImage', '')
                },
                'options': {},
                'correctAnswers': item['answers']
            }

            # Process options
            for letter, option in item['choices'].items():
                document['options'][letter] = {
                    'optionContent': option['choice_text'],
                    'optionImage': option.get('choice_image', '')
                }

            # Create an insert one operation
            bulk_operations.append(pymongo.InsertOne(document))

        # Perform bulk write
        if bulk_operations:
            # Use bulk_write for efficient insertion
            result = collection.bulk_write(bulk_operations, ordered=False)

            print(f"Inserted {result.inserted_count} documents")

        # Calculate and print execution time
        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.2f} seconds")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the MongoDB connection
        client.close()


# Usage
mongodb_uri = os.getenv('MONGODB_URI')
json_file = os.getenv('JSON_FILE')
database_name = os.getenv('DATABASE_NAME')
collection_name = os.getenv('COLLECTION_NAME')

# Call the function
bulk_insert_to_mongodb(json_file, mongodb_uri, database_name, collection_name)