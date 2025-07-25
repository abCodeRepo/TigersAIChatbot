import os
import requests

def get_course_contents(moodle_server: str, auth_token: str, course_id: int) -> dict:
	"""
	Fetch course contents from a given Moodle API.

	Args:
		moodle_server (str): The base URL of the Moodle REST API server.
		auth_token (str): The authentication token for the Moodle API.
		course_id (int): The ID of the course to retrieve the content of.

	Returns:
		dict: The response from the Moodle API, in JSON format.
	"""

	# API call parameters
	params = {
		'wstoken': auth_token,
		'wsfunction': 'core_course_get_contents',
		'courseid': course_id,
		'moodlewsrestformat': 'json'
	}

	try:
		# HTTP get for API call
		response = requests.get(moodle_server, params=params)
		response.raise_for_status()  # raise an exception for HTTP errors
		return response.json()  # return the JSON response
	except requests.exceptions.RequestException as e:
		print(f'An error occurred: {e}')
		return {'error': str(e)}

def get_moodle_file_urls(course_contents: dict) -> list:
	"""
	Extract the file URL(s) from a Moodle course contents.

	Args:
		course_contents (dict): The JSON response from the Moodle API containing the course contents.
	
	Returns:
		list: A list of file URLs extracted from the course module contents.
	"""

	#iterate through course content and append any file URLs to a list
	file_urls = []
	for section in course_contents:
		for module in section['modules']:
			if module['modname'] in ['resource', 'file']: 
				for file in module['contents']:
					file_urls.append(file['fileurl']) # the extracted file URL
	return file_urls
   
def modify_moodle_file_urls(file_urls: list, course_id:int) -> dict:
	"""
	Clean and structure Moodle file URLs by removing unneeded query parameters.

	Args:
		file_urls (list): A list of file URLs as strings, extracted from a Moodle course module contents.
	
	Returns:
		dict: A dictionary where the keys are the filenames and the values are the cleaned URLs.
	"""

	# iterate through the file urls and add the filenames and URL values to a dictionary
	modified_file_urls = {}
	for url in file_urls:
		filename = url.split('/')[-1].split('?')[0] # separate the filename from the URL
		modified_file_urls[filename]= {
			'url': url.split('?')[0], # remove the SQL query from the url (e.g ?forcedowload=1)
			'course_id': course_id
		}
	return modified_file_urls

def download_moodle_files(file_urls: list, token: str, output_dir: str = 'ingested_moodle_data'):
	"""
	Download files from Moodle using given URLs and save them to a local store.

	Args:
		file_urls (list): A list of file URLs to download data from.
		auth_token (str): The authentication token for the Moodle API.
		output_dir (str): The directory where the downloaded files will be saved. Default is 'ingested_moodle_data'.

	Returns:
		None
	"""
	
	# create the output directory if it doesn't already exist
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	for url in file_urls:
		try:
			# append the token to the file URL to create the authenticated query
			download_url = f'{url}&token={token}'
			
			# send the get request to download the file
			file_response = requests.get(download_url)
			file_response.raise_for_status()  # HTTP error check
			
			# split the filename and assign the file path
			filename = url.split('/')[-1].split('?')[0]
			filepath = os.path.join(output_dir, filename)
			
			#write the file to the given path
			with open(filepath, 'wb') as file:
				file.write(file_response.content)
			
			print(f'Downloaded: {filename}') # terminal outputs for status
		except requests.exceptions.RequestException as e:
			print(f"Failed to download {url}: {e}") # catch any failed downloads
