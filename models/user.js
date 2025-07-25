//import mongoose
const MONGOOSE = require('mongoose')

//db schema for username and password
const USERSCHEMA = new MONGOOSE.Schema({
    username: {type: String, required: true, unique: true},
    password: {type: String, required: true},
    role: { type: String, enum: ['admin', 'teacher', 'student'], required: true },
    moodleToken: {type: String},
    // list of moodle course IDs
    moodle_access: {
        courses: [{ type: String }] 
    },
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
}); 

module.exports = MONGOOSE.model('User', USERSCHEMA);