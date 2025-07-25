document.getElementById('login-form').addEventListener('submit', async (event) => {
	event.preventDefault();

	const form = event.target;
	const formData = new FormData(form);
	const data = {
		username: formData.get('username'),
		password: formData.get('password')
	};

	try {
		const response = await fetch('/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		});
		//parse the JSON
		const result = await response.json(); 

		if (result.success) {
			//redirect using the provided URL
			window.location.href = result.redirectUrl;
		} else {
			//display the error message
			const errorMessage = document.getElementById('error-message');
			errorMessage.textContent = result.message;
			errorMessage.style.display = 'block';
		}
	} catch (error) {
		console.error('Error during login:', error);
	}
});


