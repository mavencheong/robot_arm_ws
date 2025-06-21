const WebSocket = require('ws');
console.log('test')
const wss = new WebSocket.Server({ port: 8080 });

console.log('WebSocket server started on ws://localhost:8080');

wss.on('connection', (ws) => {
    console.log('Client connected');

    // Send dummy joint data every second
    // const interval = setInterval(() => {
    //     // Example joint angles (radians)
    //     const joints = {
    //         joint1: Math.sin(Date.now() / 1000),  // oscillate between -1 and 1 rad
    //         joint2: Math.cos(Date.now() / 1000),
    //         joint3: Math.sin(Date.now() / 1500),
    //     };

    //     ws.send(JSON.stringify(joints));
    // }, 1000);

    ws.on('close', () => {
        console.log('Client disconnected');
        clearInterval(interval);
    });
});
