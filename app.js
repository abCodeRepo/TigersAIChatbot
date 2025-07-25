//application base
const EXPRESS = require('express');
//mongodb interaction
const MONGOOSE = require('mongoose');
//post request handling
const BODYPARSER = require('body-parser');
//for python script integration
const { exec } = require('child_process')
const PATH = require('path');


//initialise the express application on port 3000
const APP = EXPRESS();
const PORT = 3000;

//session and auth
const SESSION = require('express-session')
const MONGOSTORE = require('connect-mongo')

//encryption and user schema
const BCRYPT = require('bcrypt');
const USER = require('./models/user'); 

//session middleware configuration
APP.use(SESSION({
	secret: 'secretkey',
	resave: false,
	saveUninitialized: false,
	store: MONGOSTORE.create({ mongoUrl: 'mongodb://localhost:27017/tigersaidb'}),
	cookie: {maxAge: 1000 * 60 * 60} //1 hour expiry
}));

//access and use html/css/js from the public directory
APP.use(EXPRESS.static('public'));

//incoming request body handler
APP.use(BODYPARSER.json());
APP.use(BODYPARSER.urlencoded({ extended: true }));







//template engine (for server side variable rendering)
APP.set('view engine', 'ejs');

//mongodb connection
MONGOOSE.connect('mongodb://localhost:27017/tigersaidb', {
	useNewUrlParser: true,
	useUnifiedTopology: true,
});

//db schema for the user messages and responses logging
const CONVERSATIONSCHEMA = new MONGOOSE.Schema({
	user_id: String,
	username: String,
	userRole: String,
	userMessage: String,
	botResponse: String,
	timestamp: {
		type: Date,
		default: Date.now },
});

//conversation collection schema
const CONVERSATION = MONGOOSE.model('conversation', CONVERSATIONSCHEMA);

//auth checking
function isAuthenticated(req, res, next) {
	//console.log("Session before authentication check:", req.session.user); //debug log

	if (req.session.user) {
		return next();
	} else {
		return res.redirect('/');
	}
}


const axios = require('axios'); // For API calls

// APP.get('/register', (req, res) => {
//     res.sendFile(PATH.join(__dirname, 'public', 'register.html'));
// });

// APP.post('/register', async (req, res) => {
//     const { username, role, password} = req.body;

	

//     // Check if username and password are provided
//     if (!username || !password) {
//         return res.status(400).send('Username and password are required');
//     }

//     // Check if the username already exists
//     const existingUser = await USER.findOne({ username });
//     if (existingUser) {
//         return res.status(409).send('Username already exists');
//     }

//     try {
//         // Hash the password
//         const hashedPassword = await BCRYPT.hash(password, 10);

//         // Create and save the user
//         const newUser = new USER({ username, role, password: hashedPassword });
//         await newUser.save();

//         res.status(201).send('User registered successfully');
//     } catch (error) {
//         console.error('Error creating user:', error);
//         res.status(500).send('Internal server error');
//     }
// });

APP.get('/login', (req, res) => {
	res.sendFile(PATH.join(__dirname, 'public', 'login.html'));
});

//login uses mongoose to check mongodb user collection data
APP.post('/login', async (req, res) => {
	const { username, password } = req.body;
	const user = await USER.findOne({ username });

	if (user && await BCRYPT.compare(password, user.password)) {
		const updatedUser = await USER.findOne({ username });
		
		req.session.user = {
			id: updatedUser._id.toString(),
			username: updatedUser.username,
			role: updatedUser.role,
			moodleToken: updatedUser.moodleToken,
			courses: updatedUser.moodle_access ? updatedUser.moodle_access.courses : []
		};

		console.log("Session Data:", req.session.user); //debug logging

		// send JSON response for successful login
		return res.json({ success: true, redirectUrl: '/chat' });
	} else {
		// send JSON response for invalid credentials
		return res.json({ success: false, message: 'Invalid credentials. Please try again.' });
	}
});


APP.post('/logout', (req, res) => {
	req.session.destroy(err => {
		if (err) return res.status(500).json({ error: 'Error logging out' });
		res.redirect('/');
	});
});


APP.get('/chat', isAuthenticated, (req, res) => {
	res.render('chat', {user: req.session.user});
});

//send message to bot route
APP.post('/chat', async(req, res) => {
	//message sent by the user
	const USERMESSAGE = req.body.userMessage;


	if (!req.session.user || !req.session.user.courses) {
		return res.status(403).json({ error: 'Unauthorized. Please log in.' });
	}

	const USERID = req.session.user.id;
	const USERNAME = req.session.user.username;
	const USERROLE = req.session.user.role; //teacher/admin/student
	const MOODLETOKEN = req.session.user.moodleToken; //user moodle access token
	const accessibleCourses = req.session.user.courses; //courses user can access

	try {
	 
		const coursesBase64 = Buffer.from(JSON.stringify(accessibleCourses)).toString('base64');
		//console.log("Courses Base64:", coursesBase64);

		exec(`python3 ${PATH.join(__dirname, 'scripts', 'langchain_response.py')} "${USERMESSAGE}" "${accessibleCourses}" "${MOODLETOKEN}"`, async (error, stdout, stderr) => {
			if (error) {
				console.error(`Error executing Python script: ${error}`);
				return res.status(500).json({ error: 'Internal Server Error' });
			}
		
			if (stderr) {
				console.error(`stderr: ${stderr}`);
			}
		
			const BOTRESPONSE = stdout.trim();
			//console.log("BOTRESPONSE:", BOTRESPONSE); // debug logging
		
			if (!BOTRESPONSE) {
				return res.status(500).json({ error: 'Bot response is empty' });
			}
		
			// save to mongodb and send back the response
			const NEWCONVERSATION = new CONVERSATION({
				user_id: USERID,
				username: USERNAME,
				userRole: USERROLE,
				userMessage: USERMESSAGE,
				botResponse: BOTRESPONSE,
				timestamp: new Date()
			});
			await NEWCONVERSATION.save();
			//console.log("Saved Conversation:", NEWCONVERSATION); //debug logging
		
			res.json({ userMessage: USERMESSAGE, botResponse: BOTRESPONSE });
		});
		
		
		
	} catch (err) {
		console.error('Error filtering contexts:', err);
		return res.status(500).json({ error: 'Internal Server Error' });
	}
});





APP.get('/calendar/conversationsByMonth', isAuthenticated, async (req, res) => {
	const USERID = req.session.user.id; // ensure the user is authenticated
	const { month } = req.query; // extract the 'month' parameter

	if (!month) {
		return res.status(400).json({ error: 'Month is required' });
	}

	try {
		// calculate the start and end dates of the given month
		const startOfMonth = new Date(month);
		const endOfMonth = new Date(startOfMonth.getFullYear(), startOfMonth.getMonth() + 1, 0);

		// fetch conversations filtered by user ID and timestamp range
		const conversations = await CONVERSATION.find({
			user_id: USERID,
			timestamp: { $gte: startOfMonth, $lte: endOfMonth }
		}).sort({ timestamp: 1 }); // sort by timestamp in ascending order

		res.json(conversations); // return the filtered conversations
	} catch (error) {
		console.error('Error fetching conversations by month:', error);
		res.status(500).json({ error: 'Internal Server Error' });
	}
});

APP.get('/calendar/conversations', isAuthenticated, async (req, res) => {
	const { date, student_id, user_id } = req.query; 
	const loggedInUser = req.session.user;

	if (!date) {
		return res.status(400).json({ error: 'Date is required' });
	}

	try {
		const selectedDate = new Date(date);
		const startOfDay = new Date(selectedDate.setHours(0, 0, 0, 0));
		const endOfDay = new Date(selectedDate.setHours(23, 59, 59, 999));

		let userIdToSearch;

		if (loggedInUser.role === 'teacher') {
			userIdToSearch = student_id ? student_id : loggedInUser.id;
		} else if (loggedInUser.role === 'student') {
			userIdToSearch = loggedInUser.id;
		} else if (loggedInUser.role === 'admin') {
			if (!user_id) {
				console.error("Admin did not select a user.");
				return res.status(400).json({ error: 'Admins must select a user.' });
			}
			userIdToSearch = user_id; 
		} else {
			return res.status(403).json({ error: 'Unauthorized access.' });
		}

		const conversations = await CONVERSATION.find({
			user_id: userIdToSearch,
			timestamp: { $gte: startOfDay, $lte: endOfDay }
		}).sort({ timestamp: 1 });

		res.json(conversations);
	} catch (error) {
		console.error('Error fetching conversations:', error);
		res.status(500).json({ error: 'Internal Server Error' });
	}
});





APP.get('/teacher/students', isAuthenticated, async (req, res) => {
	const TEACHERID = req.session.user.id;

	try {
		const teacher = await USER.findById(TEACHERID);
		if (!teacher || teacher.role !== 'teacher') {
			return res.status(403).json({ error: 'Unauthorized: Only teachers can access this feature.' });
		}

		const teacherCourses = teacher.moodle_access.courses; //get courses from the nested field

		// ensure teacherCourses is defined and is an array
		if (!Array.isArray(teacherCourses) || teacherCourses.length === 0) {
			return res.status(400).json({ error: 'Teacher has no associated courses.' });
		}

		// fetch students who share at least one course ID with the teacher
		const students = await USER.find({
			role: 'student',
			"moodle_access.courses": { $in: teacherCourses } // ue dot notation to access the nested field
		}, { username: 1, _id: 1 }); // teturn only username and _id

		res.json(students);
	} catch (error) {
		console.error('Error fetching students:', error);
		res.status(500).json({ error: 'Internal Server Error' });
	}
});

APP.get('/admin/users', isAuthenticated, async (req, res) => {
	if (!req.session.user) {
		console.error("Session Missing, Blocking Access");
		return res.status(403).json({ error: 'Unauthorized: No active session.' });
	}

	if (req.session.user.role !== 'admin') {
		console.error("Role Restriction: Not an Admin");
		return res.status(403).json({ error: 'Unauthorized: Only admins can access this feature.' });
	}
	

	try {
		const users = await USER.find({}, { username: 1, role: 1, _id: 1 });
		//console.log("Users Retrieved:", users.length); //debug logging
		res.json(users);
	} catch (error) {
		console.error('Error fetching users:', error);
		res.status(500).json({ error: 'Internal Server Error' });
	}
});

APP.get('/subnetcalculator', isAuthenticated, (req, res) => {
	res.render('subnetcalculator', {user: req.session.user});
});

APP.post('/calculateIPv4', (req, res) => {
	const ip_address = req.body.ip_address;
	const subnet_mask = req.body.subnet_mask;

	// check if the request contains valid inputs
	if (!ip_address || !subnet_mask) {
		return res.status(400).json({ error: "Missing IP address or subnet mask." });
	}

	//console.log(`Received IP: ${ip_address}, Subnet Mask: ${subnet_mask}`); debug logging

	// get the correct Python script path
	const pythonScriptPath = PATH.join(__dirname, 'scripts', 'ipv4_subnet_calculator.py');

	try {
		exec(`python3 ${pythonScriptPath} "${ip_address}" "${subnet_mask}"`, async (error, stdout, stderr) => {
			if (error) {
				console.error(`Error executing Python script: ${error.message}`);
				return res.status(500).json({ error: "Internal Server Error." });
			}
		
			if (stderr) {
				console.error(`Python STDERR: ${stderr}`);
				return res.status(500).json({ error: "Error processing subnet calculation." });
			}
		
			//console.log("Raw Python Output:", stdout.trim()); // debug to check if it's pure JSON
		
			let subnetData;
			try {
				subnetData = JSON.parse(stdout.trim()); //ensure valid JSON response
			} catch (parseError) {
				console.error("Failed to parse Python response:", parseError);
				return res.status(500).json({ error: "Invalid output from Python script." });
			}
		
			res.json(subnetData);
		});
	} catch (err) {
		console.error("Unexpected error:", err);
		return res.status(500).json({ error: "Internal Server Error." });
	}
});


APP.post('/calculateIPv6', (req, res) => {
	const ip_address = req.body.ip_address;
	const subnet_mask = req.body.subnet_mask;

	// check if the request contains valid inputs
	if (!ip_address || !subnet_mask) {
		return res.status(400).json({ error: "Missing IP address or subnet mask." });
	}

	//console.log(`Received IP: ${ip_address}, Subnet Mask: ${subnet_mask}`); debug logging

	// get the correct Python script path
	const pythonScriptPath = PATH.join(__dirname, 'scripts', 'ipv6_subnet_calculator.py');

	try {
		exec(`python3 ${pythonScriptPath} "${ip_address}" "${subnet_mask}"`, async (error, stdout, stderr) => {
			if (error) {
				console.error(`Error executing Python script: ${error.message}`);
				return res.status(500).json({ error: "Internal Server Error." });
			}
		
			if (stderr) {
				console.error(`Python STDERR: ${stderr}`);
				return res.status(500).json({ error: "Error processing subnet calculation." });
			}
		
			//console.log("Raw Python Output:", stdout.trim()); // debug to check if it's pure JSON
		
			let subnetData;
			try {
				subnetData = JSON.parse(stdout.trim()); // ensure valid JSON response
			} catch (parseError) {
				console.error("Failed to parse Python response:", parseError);
				return res.status(500).json({ error: "Invalid output from Python script." });
			}
		
			res.json(subnetData);
		});
	} catch (err) {
		console.error("Unexpected error:", err);
		return res.status(500).json({ error: "Internal Server Error." });
	}
});


const serverTimestamp = new Date();

APP.listen(3000, () => {
	console.log("Server for TigersAI started on port 3000 (localhost:3000)");
	console.log(serverTimestamp);
});


