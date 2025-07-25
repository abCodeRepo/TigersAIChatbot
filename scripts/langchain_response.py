import sys
import os
import json
import base64
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from better_profanity import profanity
from dotenv import load_dotenv
from modules.prompting import get_hardcoded_responses


load_dotenv()

# Globals for Moodle server connection
MOODLE_AUTH_TOKEN: str = os.getenv("MOODLE_AUTH_TOKEN")

VECTOR_DB_DIR = "faiss_index"

#initialize profanity filter
profanity.load_censor_words()

#set up an optional prompt template, not needed at the moment but can be
#used for precision
QA_PROMPT = PromptTemplate(
	input_variables=["context", "question"],
	template="""
	Context:
	{context}

	Question: {question}

	Answer:"""
)

def qa_with_retriever(query: str, accessible_courses: list, token: str)-> str:
	"""
	Retrieves and answers a user query based on accessible course content using a retrieval-based QA chain.

	Args:
		query (str): The user's input question
		accessible_courses (list): A list of course IDs the user has access to.
		token (str): The users moodle access token.

	Returns:
		str: A markdown-formatted string containing the generated answer and a list of source URLs.
	"""
	embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
	db = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)

	retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 10})
	all_docs = retriever.get_relevant_documents(query)

	# Filter retrieved documents
	filtered_docs = [doc for doc in all_docs if any(course in doc.metadata.get("course_id", "") for course in accessible_courses)]

	if not filtered_docs:
		print("Response: No relevant content found for your accessible courses.")
		return "Sorry, I couldn't find relevant information."

	llm = Ollama(model="llama3.2:3b")
	qa_chain = RetrievalQA.from_chain_type(
		llm=llm,
		retriever=retriever,  #retriever
		return_source_documents=True,
		chain_type_kwargs={"prompt": QA_PROMPT}
	)

	# pass the filtered documents as `input_documents`
	response = qa_chain.combine_documents_chain.run(input_documents=filtered_docs, question=query)

	# print unique Moodle sources
	seen_urls = set(doc.metadata.get("moodle_url", "") for doc in filtered_docs)

	# format response as markdown
	formatted_response = f"**Answer:**\n\n{response.strip()}\n\n"
	formatted_response += "### Moodle Sources:\n"
	for url in seen_urls:
		if url:
			# append token
			if '?' in url:
				url_with_token = f"{url}&token={token}"
			else:
				url_with_token = f"{url}?token={token}"
			formatted_response += f"- [{url_with_token}]({url_with_token})\n"
	print(formatted_response)
	return formatted_response  # return Markdown formatted response

#basic profanity filter
def profanity_filter(query: str) -> bool:
	"""
	Takes the user query and validates whether it contains profanity.

	Args:
		query (str): The user's input question

	Returns:
		bool: True if profanity is parsed, False otherwise.
	"""
	if profanity.contains_profanity(query):
		print("I'm sorry, I can't respond to that request.")
		return True
	return False


if __name__ == "__main__":
	query = sys.argv[1]
	#profanity filtering
	if profanity_filter(query):
		sys.exit(0)
	#hardcoded response filtering
	hardcoded_responses = get_hardcoded_responses()
	lower_query = query.lower().strip()
	if lower_query in hardcoded_responses:
		print(f"<p>{hardcoded_responses[lower_query]}</p>")
		sys.exit(0)
	#llm response
	accessible_courses = sys.argv[2]
	#accessible_courses = json.loads(base64.b64decode(base64_courses).decode("utf-8"))
	moodle_token = sys.argv[3]
	qa_with_retriever(query, accessible_courses, moodle_token)
	