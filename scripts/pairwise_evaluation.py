import sys
import os
import json
import base64
from typing import Tuple
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.evaluation import PairwiseStringEvaluator

#use the previously made vector embedding directory
VECTOR_DB_DIR = "faiss_index"

#set up a prompt template for the llm
QA_PROMPT = PromptTemplate(
	input_variables=["context", "question"],
	template="""Context:
	{context}

	Question: {question}

	Answer:"""
)

#make a retriever using FAISS, using the same embedding model, using similarity
def get_retriever(index_dir, k=10):
	"""Create a retriever using FAISS index."""
	embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
	db = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
	return db.as_retriever(search_type="similarity", search_kwargs={"k": k})


#get all documents (no need to filter by course) and use an LLM (llama3.2:3b) two generate a response to a prompt
def get_answer_from_retriever(retriever, query, accessible_courses=None):
	# retrieve documents
	all_docs = retriever.get_relevant_documents(query)

	# filter documents by accessible courses if needed (defaults to none)
	if accessible_courses:
		all_docs = [doc for doc in all_docs if any(course in doc.metadata.get("course_id", "") for course in accessible_courses)]

	if not all_docs:
		print("Response: No relevant content found.")
		return "Sorry, could not find relevant information for your question."

	# llm to generate answer
	llm = Ollama(model="llama3.2:3b")
	qa_chain = RetrievalQA.from_chain_type(
		llm=llm,
		retriever=retriever,
		return_source_documents=True,
		chain_type_kwargs={"prompt": QA_PROMPT}
	)

	# generate the answer
	response = qa_chain.combine_documents_chain.run(input_documents=all_docs, question=query)
	return response.strip()



#evaluator class for a pairwise response (two reponses), uses langchains pairwisestringevaluator as a base
class LLMBasedPairwiseEvaluator(PairwiseStringEvaluator):
	def __init__(self, llm=None):
		# use a default local llm if no llm provided as argument
		self.llm = llm or Ollama(model="llama3.2:3b")
	
	#evaluate two responses against each other
	def _evaluate_string_pairs(self, response_pair: Tuple[str, str], query: str, context: str) -> Tuple[float, str]:
		answer_1, answer_2 = response_pair
		# Need to build a prompt that instructs the llm to output a JSON with two keys
		# "score" a float between 0 and 1, and "explanation" a string explaining its decision
		prompt = f"""
			You are an impartial evaluator. Evaluate the quality of the following two answers given a query and context.
			Consider correctness, detail, and relevance. Produce your output as a JSON object with two keys:
			- "score": A number between 0 and 1 where 1 indicates that Answer 1 is clearly better than Answer 2, and 0 indicates vice versa.
			- "explanation": A brief explanation for your scoring decision.
			Do not output any additional text.

			Query: {query}

			Context: {context}

			Answer 1: {answer_1}

			Answer 2: {answer_2}

			Your output:
			"""
		# call the llm with the prompt structure above
		result = self.llm(prompt)

		# parse the output as json and return it as the score and explanation
		try:
			parsed = json.loads(result)
			score = float(parsed["score"])
			explanation = str(parsed["explanation"])

			# ensure the score is in the [0, 1] range
			score = max(0.0, min(1.0, score))
			return score, explanation
		except Exception as e:
			raise ValueError(f"Failed to parse LLM output into a float and explanation. Received output: {result}. Error: {str(e)}")
		
	# wrapper for the evaluate_string_pairs method
	def evaluate(self, query: str, context: str, response_1: str, response_2: str) -> Tuple[float, str]:
		return self._evaluate_string_pairs((response_1, response_2), query, context)

def qa_with_pairwise_evaluation(query: str, accessible_courses: list):
	# create two different retrievers with different params
	retriever_1 = get_retriever(VECTOR_DB_DIR, k=10)  # default retriever
	retriever_2 = get_retriever(VECTOR_DB_DIR, k=5)  # another retriever with fewer results to work with

	# get llm response from both retrievers
	answer_1 = get_answer_from_retriever(retriever_1, query, accessible_courses=None)
	answer_2 = get_answer_from_retriever(retriever_2, query, accessible_courses=None)

	# instantiate the llmbasedpairwiseevaluator class
	evaluator = LLMBasedPairwiseEvaluator()

	# evaluate both responses
	score, explanation = evaluator.evaluate(
		query=query,
		context="Context for comparison between the answers",
		response_1=answer_1,
		response_2=answer_2
	)

	print(f"Evaluation score: {score}")
	print(f"Evaluator explanation: {explanation}")
	
	#over 0.5 is answer 1 (k=10), below is answer 2 (k=5)
	if score > 0.5:
		print("Answer 1 is chosen as the better response.")
		chosen_response = answer_1
		unchosen_response = answer_2
	else:
		print("Answer 2 is chosen as the better response.")
		chosen_response = answer_2
		unchosen_response = answer_1

	return chosen_response, unchosen_response, score, explanation


if __name__ == "__main__":
	query = "What are the differences between TCP and UDP, and when should you use each?"
	accessible_courses = ""
	chosen_answer, unchosen_answer, evaluation_score, evaluator_explanation = qa_with_pairwise_evaluation(query, accessible_courses)
	
	# build a dictionary with the evaluation results for json output
	new_entry = {
		"question": query,
		"evaluation_score": evaluation_score,
		"explanation": evaluator_explanation,
		"chosen_answer": chosen_answer,
		"unchosen_answer": unchosen_answer
	}

	output_filename = "pairwise_evaluation_result.json"
	
	# check if file exists
	if os.path.exists(output_filename):
		with open(output_filename, "r") as infile:
			try:
				existing_data = json.load(infile)
				# check data is a list
				if not isinstance(existing_data, list):
					existing_data = [existing_data]
			except json.JSONDecodeError:
				existing_data = []
	else:
		existing_data = []
	
	# append the new evaluation entry
	existing_data.append(new_entry)

	with open(output_filename, "w") as outfile:
		json.dump(existing_data, outfile, indent=4)
	
	print(f"Evaluation results appended to {output_filename}")