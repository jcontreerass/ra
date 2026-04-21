var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var serveIndex = require('serve-index');
const mqtt = require('mqtt');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

// Configuración MQTT
const mqttClient = mqtt.connect('mqtt://localhost');

mqttClient.on('connect', () => {
    console.log('Connected to Mosquitto broker');
});

mqttClient.on('error', (err) => {
    console.error('MQTT Connection error:', err);
});

// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Middleware
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// API Endpoint para sensores
app.post('/api/datos', (req, res) => {
    const data = req.body;

    // Publicar cada clave del JSON en un tópico distinto
    Object.keys(data).forEach((key) => {
        const topic = `sensores/${key}`;
        const payload = data[key].toString();

        mqttClient.publish(topic, payload, { qos: 1 }, (err) => {
            if (err) {
                console.error(`Failed to publish to ${topic}`, err);
            }
        });
    });

    console.log('Data routed to MQTT topics:', data);

    res.status(201).json({
        status: "success",
        delivered: data
    });
});

// Routes
app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/logs', serveIndex(path.join(__dirname, 'public/logs')));
app.use('/logs', express.static(path.join(__dirname, 'public/logs')));

// Catch 404
app.use(function(req, res, next) {
    next(createError(404));
});

// Error handler
app.use(function(err, req, res, next) {
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    res.status(err.status || 500);
    res.render('error');
});

app.listen(3001, () => {
    console.log('Server listening on port 3000');
});

module.exports = app;
