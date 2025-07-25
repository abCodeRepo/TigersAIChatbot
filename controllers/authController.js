const User = require('../models/User');
const bcrypt = require('bcrypt');

exports.login = async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (user && await bcrypt.compare(password, user.password)) {
        req.session.user = { id: user._id, username: user.username };
        res.redirect('/chat');
    } else {
        res.status(401).send('Invalid credentials');
    }
};
