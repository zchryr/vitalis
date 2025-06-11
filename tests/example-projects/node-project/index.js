const express = require('express');
const axios = require('axios');
const _ = require('lodash');
const moment = require('moment');

const app = express();
const port = 3000;

app.get('/', async (req, res) => {
    try {
        const response = await axios.get('https://api.github.com/users/github');
        const data = _.pick(response.data, ['login', 'id', 'name']);
        data.timestamp = moment().format();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});