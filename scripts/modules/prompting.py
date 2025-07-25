from typing import List, Dict
import datetime

def get_hardcoded_responses() -> Dict[str, str]:
    return {
        "hello": "I'm TigersAI, a chatbot assistant. Please ask me a question and I'll see if I can help!",
        "hi": "I'm TigersAI, a chatbot assistant. Please ask me a question and I'll see if I can help!",
        "hey": "I'm TigersAI, a chatbot assistant. Please ask me a question and I'll see if I can help!",
        "how are you": "I'm just a bot, but thanks for asking! How can I assist you?",
        "how are you?": "I'm just a bot, but thanks for asking! How can I assist you?",
        "what is the current date?": f"{datetime.datetime.now()}",
        "what is the current date": f"{datetime.datetime.now()}",
        "what is the current time?": f"{datetime.datetime.now()}",
        "what is the current time": f"{datetime.datetime.now()}"
        #etc
    }

def get_anchor_points_and_negatives() -> Dict[str, Dict[str, List[str]]]:
    return {
        'download': {
            'anchor_points': [
                'provide a download url link if available',
                'provide succint steps for installation',
                'url links must be in lower case',
            ],
            'negative_examples': [
                'Do not provide a definition of the topic.',
                'Avoid explaining what the topic is.',
            ]
        },
        'install': {
            'anchor_points': [
                'provide a download url link if available',
                'provide succint steps for installation',
                'any url link must be given verbatim and unmodified',
            ],
            'negative_examples': [
                'Do not provide a definition of the topic.',
                'Avoid explaining what the topic is.',
            ]
        },
        'Network Configuration': {
            'anchor_points': [
                'Network configuration steps:',
                'Steps to configure network addresses:',
            ],
            'negative_examples': [
                'Do not provide a definition of network configuration.',
                'Avoid explaining what network configuration is.',
            ]
        }
    }

def modify_prompt(user_prompt: str, anchor_points_and_negatives: dict, base_prompt: str = None):
    #check for keywords in user query
    prompt_topic = None
    for topic in anchor_points_and_negatives:
        if topic in user_prompt.lower():
            prompt_topic = topic
            break
    
    if prompt_topic:
        anchors = ' '.join(anchor_points_and_negatives[prompt_topic]['anchor_points'])
        negatives = ' '.join(anchor_points_and_negatives[prompt_topic]['negative_examples'])
        modified_prompt = f'{anchors} {negatives} {user_prompt}'
        return modified_prompt
    else:
        return user_prompt