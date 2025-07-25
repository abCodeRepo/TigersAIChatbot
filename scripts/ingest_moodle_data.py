from modules.moodle_functions import get_course_contents, get_moodle_file_urls, modify_moodle_file_urls, download_moodle_files
from dotenv import load_dotenv
import os
import json

#load env vars
load_dotenv()

# globals for Moodle server connection
MOODLE_SERVER: str = os.getenv("MOODLE_SERVER")
MOODLE_AUTH_TOKEN: str = os.getenv("MOODLE_AUTH_TOKEN")
MOODLE_COURSE_ID: int = os.getenv("MOODLE_COURSE_ID")

if __name__ == "__main__":
	course_contents = get_course_contents(MOODLE_SERVER, MOODLE_AUTH_TOKEN, MOODLE_COURSE_ID)
	moodle_file_urls = get_moodle_file_urls(course_contents)
	modified_moodle_file_urls = modify_moodle_file_urls(moodle_file_urls, MOODLE_COURSE_ID)
	print(modified_moodle_file_urls)
	with open("moodle_file_metadata.json", "w") as f:
		json.dump(modified_moodle_file_urls, f, indent=4)
	download_moodle_files(moodle_file_urls, MOODLE_AUTH_TOKEN)
	
