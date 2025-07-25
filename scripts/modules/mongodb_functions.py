import os
import logging
from typing import List, Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import numpy as np
from numpy.typing import NDArray
from dotenv import load_dotenv


load_dotenv()

MONGODB_SERVER: str = os.getenv('MONGODB_SERVER') #e.g., "localhost:27017"
MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE') #e.g., "mydatabase"
MONGODB_COLLECTION_EMBEDDINGS: str = os.getenv('MONGODB_COLLECTION_CONTEXTEMBEDDINGS') # e.g., "embeddings"
MONGODB_COLLECTION_CONVERSATIONS: str = os.getenv('MONGODB_COLLECTION_CONVERSATIONS')  # e.g., "conversations"
MONGODB_COLLECTION_USERS: str = os.getenv('MONGODB_COLLECTION_USERS')  # e.g., "users"


def mongodb_connection(db_name: str, collection_name: str, connection_string: str = MONGODB_SERVER) -> object:
	"""
	Establish a connection to a MongoDB collection

	Args:
		db_name (str): Name of the MongoDB database to connect to.
		collection_name (str): Name of the collection within the MongoDB database.
		connection_string (str): The MongoDB connection URL string (defaults to localhost on port 27017)

	Returns:
		Collection (object): The collection database connection.    
	"""
	try:
		# establish MongoDB client connection
		client = MongoClient(connection_string)

		# check the initial connection before going further
		# primary node/main node refers to read and write node (secondary nodes are read only)
		if not client.is_primary:
			raise ConnectionError('Failed to connect to MongoDB server. Server cannot be reached.')

		# access the database and the collection
		db = client[db_name]
		collection = db[collection_name]

		return collection    
	except ConnectionFailure as e:
		logging.error(f'Connection Error: {e}')

def store_data_in_mongodb(context_data: List[Dict[str, str]], context_embeddings: NDArray[np.float32]) -> None:
	"""
	Store context data and embeddings in MongoDB.

	Args:
		context_data (List[Dict[str, str]]): Contextual data with text and URLs.
		context_embeddings (NDArray[np.float32]): Corresponding vectorised context embeddings.

	Returns:
		None
	"""

	try:
		# mongodb collection connection
		collection = mongodb_connection(MONGODB_DATABASE, MONGODB_COLLECTION_EMBEDDINGS)

		# insert context data and corresponding embeddings into MongoDB
		for idx, context in enumerate(context_data):#
			document = {   
				'context': context['context'],
				'moodle_url': context['moodle_url'],
				'course_id': context['course_id'],
				'embedding': context_embeddings[idx].tolist(),
				'createdAt': __import__('datetime').datetime.utcnow()
			}
			collection.insert_one(document)
		print('Context embeddings stored successfully in MongoDB.') # terminal message
	# error handling
	except ConnectionError as e:
		logging.error(f'Connection Error: {e}')
	except Exception as e:
		logging.error(f'The following error occurred while storing data: {e}')