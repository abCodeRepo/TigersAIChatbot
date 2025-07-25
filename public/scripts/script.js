//send prompt button (enter works fine too)
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-message').addEventListener('keypress', function(e) {
	if (e.key === 'Enter') {
		sendMessage();
	}
});

document.addEventListener("DOMContentLoaded", () => {
	//console.log("Sidebar script loaded!"); // debugging step

	const sidebarToggler = document.querySelector('.sidebar-toggler');
	const sidebar = document.querySelector('.sidebar');

	if (sidebarToggler && sidebar) {
		sidebarToggler.addEventListener('click', () => {
			//console.log("Sidebar toggle clicked!"); // debugging step
			sidebar.classList.toggle('active'); // Toggle visibility
		});
	} else {
		console.error("Sidebar elements not found!"); // if sidebar is missing
	}
});



//check to see if a message has been sent (for background image)
let isFirstMessage = true;

//send the message
function sendMessage() {
	// get the input field and send button divs
	const userInputField = document.getElementById('user-message');
	const sendButton = document.getElementById('send-button');
	//get the value of the message
	const USERMESSAGE = document.getElementById('user-message').value;
	if (USERMESSAGE.trim() === '') return;

	// disable input field and send button divs until response comes back
	userInputField.disabled = true;
	sendButton.disabled = true;

	//when first message sent, remove background image
	if (isFirstMessage) {
		document.getElementById('chat-container').style.backgroundImage = 'none';
		isFirstMessage = false;
	}

	displayMessage(USERMESSAGE, 'user');

	//clear the input box after user presses key
	document.getElementById('user-message').value = '';

	// display "processing..." message
	const PROCESSINGELEMENT = displayProcessingMessage();

	//send the user message as post the the backend as json
	fetch('http://localhost:3000/chat', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ userMessage: USERMESSAGE })
	})
	.then(response => response.json())
	.then(data => {
		//console.log('Response Data:', data);  // debug log the response data
		//remove "Processing..." message
		PROCESSINGELEMENT.remove();
		displayMessage(data.botResponse, 'bot');
	})
	.catch(error => {
		console.error('Error:', error);
	})
	.finally(() => {
		// re-enable input field and send button
		userInputField.disabled = false;
		sendButton.disabled = false;

		// Ffcus back to the input field
		userInputField.focus();
	});
}

//each time a message gets sent, add a div to create a chat like layout
function displayMessage(message, sender) {
	const MESSAGEELEMENT = document.createElement('div');
	MESSAGEELEMENT.classList.add(sender === 'user' ? 'user-message' : 'bot-response');
	
	// handle bot responses as HTML
	if (sender === 'bot') {
		const HEADER = document.createElement('div');
		HEADER.style.display = 'flex';
		HEADER.style.alignItems = 'center';
		HEADER.style.marginBottom = '10px';

		const LOGO = document.createElement('img');
		LOGO.src = '/assets/img/tiger2.svg'; 
		LOGO.alt = 'TigersAI Logo';
		LOGO.style.width = '24px';
		LOGO.style.height = '24px';
		LOGO.style.marginRight = '10px';

		const HEADER_TEXT = document.createElement('span');
		HEADER_TEXT.textContent = 'TigersAI';
		HEADER_TEXT.style.fontWeight = 'bold';

		HEADER.appendChild(LOGO);
		HEADER.appendChild(HEADER_TEXT);

		const HR = document.createElement('hr');
		HR.style.margin = '10px 0';
		HR.style.borderColor = '#ddd';

		MESSAGEELEMENT.appendChild(HEADER);
		MESSAGEELEMENT.appendChild(HR);

		// convert Markdown to HTML using `marked` library
		const RESPONSE_TEXT = document.createElement('div');
		RESPONSE_TEXT.innerHTML = marked.parse(message);
		MESSAGEELEMENT.appendChild(RESPONSE_TEXT);
	} else {
		MESSAGEELEMENT.textContent = message;
	}

	document.getElementById('messages').appendChild(MESSAGEELEMENT);

	window.scrollTo({
		top: document.body.scrollHeight, // scrolls to the very bottom of the page
		behavior: 'smooth'
	});

	return MESSAGEELEMENT;
}

//display an animated "processing..." message 
function displayProcessingMessage() {
	//add to bot response div
	const PROCESSINGELEMENT = document.createElement('div');
	PROCESSINGELEMENT.classList.add('bot-response');
	
	//the text itself
	const PROCESSINGTEXT = document.createElement('span');
	PROCESSINGTEXT.textContent = "Processing";
	PROCESSINGELEMENT.appendChild(PROCESSINGTEXT);
	
	//the animation
	const DOTS = document.createElement('span');
	DOTS.classList.add('bot-processing-animation');
	const SPAN1 = document.createElement('span');
	const SPAN2 = document.createElement('span');
	const SPAN3 = document.createElement('span');
	DOTS.appendChild(SPAN1);
	DOTS.appendChild(SPAN2);
	DOTS.appendChild(SPAN3);
	PROCESSINGELEMENT.appendChild(DOTS);
	document.getElementById('messages').appendChild(PROCESSINGELEMENT);  

	return PROCESSINGELEMENT;
}

let calendar;

document.addEventListener('DOMContentLoaded', function () {
	const calendarEl = document.getElementById('calendar');
	let liveChatMessages = []; // store session live chat messages 
	let isSessionSaved = false; // track if session data has already been saved

	calendar = new FullCalendar.Calendar(calendarEl, {
		initialView: 'dayGridMonth',
		events: async function (fetchInfo, successCallback, failureCallback) {
			try {
				const response = await fetch(`/calendar/conversationsByMonth?month=${fetchInfo.start.toISOString()}`);
				const conversations = await response.json();

				const events = conversations.map(conversation => ({
					title: conversation.userMessage,
					start: conversation.timestamp,
					extendedProps: {
						botResponse: conversation.botResponse
					}
				}));

				successCallback(events);
			} catch (error) {
				console.error('Error fetching conversation events:', error);
				failureCallback(error);
			}
		},
		dateClick: async function (info) {
			const selectedDate = info.dateStr;

			calendar.getEvents().forEach(event => {
				if (event.extendedProps && event.extendedProps.isHighlight) {
					event.remove();
				}
			});

			calendar.addEvent({
				start: selectedDate,
				display: 'background',
				classNames: ['highlighted-date'],
				extendedProps: {
					isHighlight: true
				}
			});


	// fetch selected student (for teachers) or user (for admins)
	const studentFilter = document.getElementById('student-filter');
	const userFilter = document.getElementById('user-filter');

	let selectedStudentId = sessionStorage.getItem('selectedStudentId'); // retrieve stored student selection
	let selectedUserId = sessionStorage.getItem('selectedUserId'); // retrieve stored user selection

	console.log("Selected Date:", selectedDate);
	console.log("Stored Student ID:", selectedStudentId);
	console.log("Stored User ID (Admin):", selectedUserId);

	let url;

	if (window.userRole === 'teacher') {
		url = selectedStudentId 
			? `/calendar/conversations?date=${selectedDate}&student_id=${selectedStudentId}` 
			: `/calendar/conversations?date=${selectedDate}&student_id=${window.userId}`; 
		} else if (window.userRole  === 'admin') {
			url = selectedUserId 
			? `/calendar/conversations?date=${selectedDate}&user_id=${selectedUserId}` 
			: null; // admins must select a user
		} else if (window.userRole  === 'student') {
			url = `/calendar/conversations?date=${selectedDate}&student_id=${window.userId}`; // students fetch their own logs
		}

		if (!url) {
			console.warn("No valid selection—cannot fetch logs.");
		return;
		}

		console.log("Fetching Conversations from URL:", url);

		try {
			const response = await fetch(url);
			const conversations = await response.json();

			console.log(`Fetched Conversations Count: ${conversations.length}`);
			switchToDateView(conversations, selectedDate);
		} catch (error) {
			console.error('Error fetching conversations:', error);
		}
	}
});

	calendar.render();

	/* switches to the date-specific view in the chat window. Disables input for new prompts 
	and replaces content with the selected date's conversations.*/
	function switchToDateView(conversations, date) {
		const messagesContainer = document.getElementById('messages');
		const userInputContainer = document.getElementById('user-input-container');
		const chatContainer = document.getElementById('chat-container');

		// save live chat messages only once
		if (!isSessionSaved) {
			liveChatMessages.length = 0; // clear the array
			Array.from(messagesContainer.children).forEach(child => {
				if (child.className === 'user-message') {
					liveChatMessages.push({
						type: 'user',
						text: child.innerText,
						html: child.innerHTML
					});
				} else if (child.className === 'bot-response') {
					liveChatMessages.push({
						type: 'bot',
						text: child.innerText,
						html: child.innerHTML
					});
				}
			});
			isSessionSaved = true; //mark session data as saved
		}

		//clear chat window and add a "Back to Live Chat" button
		messagesContainer.innerHTML = `<button id="back-to-live-chat" class="btn btn-secondary">Back to Live Chat</button>`;

		// remove background logo
		chatContainer.style.backgroundImage = 'none';

		// display conversations for the selected date
		if (conversations.length > 0) {
			conversations.forEach(conversation => {
				const userMessage = document.createElement('div');
				userMessage.className = 'user-message';
				userMessage.innerText = conversation.userMessage;

				const botResponse = document.createElement('div');
				botResponse.className = 'bot-response';
				botResponse.innerHTML = marked.parse(conversation.botResponse);

				messagesContainer.appendChild(userMessage);
				messagesContainer.appendChild(botResponse);
			});
		} else {
			const noConvoMsg = document.createElement('div');
			noConvoMsg.textContent = 'No conversations found for the selected date.';
			noConvoMsg.classList.add('no-conversations');
			messagesContainer.appendChild(noConvoMsg);

		}

		// disable user input
		userInputContainer.style.display = 'none';

		// add on click for "back to live chat" button
		document.getElementById('back-to-live-chat').addEventListener('click', function () {
			switchToLiveChatView();
		});
	}

	/*switches back to the live chat view. Enables input for new prompts 
	again */
	function switchToLiveChatView() {
		const messagesContainer = document.getElementById('messages');
		const userInputContainer = document.getElementById('user-input-container');
		const chatBox = document.getElementById('chat-box');

		// remove calendar highlight
		calendar.getEvents().forEach(event => {
			if (event.extendedProps && event.extendedProps.isHighlight) {
				event.remove();
			}
		});

		// clear the chat window and reset live chat view
		messagesContainer.innerHTML = '';
		userInputContainer.style.display = 'flex';

		// restore live chat messages
		liveChatMessages.forEach(message => {
			const messageElement = document.createElement('div');
			messageElement.className = message.type === 'user' ? 'user-message' : 'bot-response';
			//messageElement.innerText = message.text;
			messageElement.innerHTML = marked.parse(message.html)
			messagesContainer.appendChild(messageElement);
		});

		isSessionSaved = false; // reset the flag to allow future saving if needed
	}
});
document.addEventListener('DOMContentLoaded', async function () {
const userFilterContainer = document.getElementById('user-filter-container');
const userRole = window.userRole; 

if (window.userRole === 'teacher' || window.userRole === 'admin') {
userFilterContainer.style.display = 'block';

try {
	//get correct user data based on role
	const response = await fetch(userRole === 'admin' ? '/admin/users' : '/teacher/students');
	if (!response.ok) {
		console.error(`Failed to fetch ${userRole === 'admin' ? 'users' : 'students'}:`, response.statusText);
		return;
	}

	const users = await response.json();
	const userFilter = document.getElementById('user-filter');

	users.forEach(user => {
		const option = document.createElement('option');
		option.value = user._id;
		option.textContent = user.username;
		userFilter.appendChild(option);
	});

	// check selections are stored
	userFilter.addEventListener('change', function () {
		const selectedUserId = userFilter.value;
		if (userRole === 'teacher') {
			sessionStorage.setItem('selectedStudentId', selectedUserId);
			console.log("Stored Student ID:", selectedUserId);
		} else if (userRole === 'admin') {
			sessionStorage.setItem('selectedUserId', selectedUserId);
			console.log("Stored User ID:", selectedUserId);
		}
	});
} catch (error) {
	console.error(`Error fetching ${userRole === 'admin' ? 'users' : 'students'}:`, error);
}
}
});




