import os
import json
import hashlib
from typing import List, Dict
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

# load const vars
EMBED_MODEL = "BAAI/bge-small-en"
DOCS_DIR = "ingested_moodle_data"
VECTOR_DB_DIR = "faiss_index"
MANIFEST_PATH = "document_manifest.json"

# load metadata from json file
with open("moodle_file_metadata.json", "r") as f:
	moodle_metadata = json.load(f)


def hash_file(path: str) -> str:
	"""
	Takes a given file path and generates an md5 hash checksum

	Args:
		path (str): The file path of the file to be hashed.

	Returns:
		str: A charset of hexidecimal digits representing the hashed value.
	"""
	with open(path, "rb") as f:
		return hashlib.md5(f.read()).hexdigest()

def load_manifest(path: str) -> Dict[str, str]:
	"""
	Takes a given file path and loads the JSON data of that file.

	Args:
		path (str): The file path of the JSON file to be loaded.

	Returns:
		dictionary (dict[str, str]): A JSON dictionary of the content of the file.
	"""
	if os.path.exists(path):
		with open(path, "r") as f:
			return json.load(f)
	return {}

def save_manifest(manifest: Dict[str, str], path: str):
	"""
	Takes a Dictionary of String: String Key:Value pairs, and a file path and writes
	the dictionary to that path as a JSON dictionary.

	Args:
		manifest (Dict[str:str]): The dictionary containing the stringified key:value pairs.
		path (str): The file path location to save the dictionary to.

	Returns:
		None
	"""
	with open(path, "w") as f:
		json.dump(manifest, f, indent=2)

def load_and_split_new_docs(doc_folder: str, manifest: Dict[str, str], metadata_dict: Dict[str, Dict[str, str]]) -> List[Document]:
	"""
	Retrieves document files from a specified folder and a metadata dictionary, parses the content using the Unstructured library,
	attaches relevant metadata and performs recursive character splitting into overlapping chunks to assist with retrieval via a
	large language model.

	Args:
		doc_folder (str): The directory path to load documents from.
		manifest (Dict[str:str]): The dictionary containing the stringified key:value pairs.
		metadata_dict (Dict[str, Dict[str:str]]): A nested dictionary containing metadata for the documents within the doc_folder directory path.

	Returns:
		Document (List): A LangChain representation of the documents as a list storing both text and metadata.
	"""
	new_docs = []
	for file in os.listdir(doc_folder):
		if not file.endswith((".pdf", ".docx")):
			continue
		path = os.path.join(doc_folder, file)
		file_hash = hash_file(path)

		if manifest.get(file) == file_hash:
			print(f"Skipping unchanged file: {file}")
			continue

		print(f"Processing new or changed file: {file}")
		loader = UnstructuredFileLoader(path)
		docs = loader.load()

		# attach Moodle metadata
		moodle_info = metadata_dict.get(file, {})
		for doc in docs:
			doc.metadata["moodle_url"] = moodle_info.get("url", file)
			doc.metadata["course_id"] = moodle_info.get("course_id", "unknown")

		new_docs.extend(docs)
		manifest[file] = file_hash  # update manifest


	# chunk the documents
	splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
	return splitter.split_documents(new_docs)

def embed_and_store(docs: List[Document]):
	"""
	Checks the document list against the existing documents. If a document does not exist performs embedding using a
	given embedding model. Creates an index file for FAISS and saves the embedded documents into the FAISS vector
	index.

	Args:
		docs (List[Document]): A LangChain representation of the documents as a list storing both text and metadata.

	Returns:
		None
	"""
	if not docs:
		print("No new documents to embed.")
		return

	embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

	# load or create FAISS index
	if os.path.exists(os.path.join(VECTOR_DB_DIR, "index.faiss")):
		db = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
		db.add_documents(docs)
	else:
		db = FAISS.from_documents(docs, embeddings)

	db.save_local(VECTOR_DB_DIR)
	print(f"Embedded and stored {len(docs)} documents in FAISS.")

if __name__ == "__main__":
	# load manifest and Moodle metadata
	manifest = load_manifest(MANIFEST_PATH)

	with open("moodle_file_metadata.json", "r") as f:
		moodle_metadata = json.load(f)

	# embed only new or changed files
	new_docs = load_and_split_new_docs(DOCS_DIR, manifest, moodle_metadata)
	embed_and_store(new_docs)
	save_manifest(manifest, MANIFEST_PATH)

