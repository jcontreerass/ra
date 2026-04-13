var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  var port = req.socket.localPort;
  port = port % 3000 + 1;
  
  res.send("You are in the server " + port + '\nrespond with a resource');
});

module.exports = router;
