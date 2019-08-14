var PORT = 1234;
var BROADCAST_ADDR = "0.0.0.0";
var dgram = require('dgram'); 
var server = dgram.createSocket("udp4"); 

server.bind(function() {
    server.setBroadcast(true);
    setInterval(broadcastNew, 3000);
});

function broadcastNew() {
    var message = Buffer.from("Broadcast message!");
    server.send(message, 0, message.length, PORT, BROADCAST_ADDR, function() {
        console.log("Sent '" + message + "'");
    });
}