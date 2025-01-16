const net = require("net");

const flaskHost = process.env.FLASK_HOST || "localhost";
const flaskPort = process.env.FLASK_PORT || 4001;
const denoHost = process.env.DENO_HOST || "localhost";
const denoPort = process.env.DENO_PORT || 4002;

const hackerResponse = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHacker!"

const server = net.createServer((clientSocket) => {

    const flaskSocket = new net.Socket();
    const denoSocket = new net.Socket();
    flaskSocket.connect(flaskPort, flaskHost);
    denoSocket.connect(denoPort, denoHost);

    const end = () => {
        if (flaskResponse.includes("Hacker!") || flaskResponse.slice(0,15) !== "HTTP/1.1 200 OK") {
            clientSocket.write(hackerResponse);
            clientSocket.end();
        } else {
            clientSocket.write(denoResponse);
            clientSocket.end();
        }
    }


    clientSocket.on("data", (data) => {
        const request = data.toString();
        
        if (/[^\x00-\x7F]/.test(request) || request.includes("%")) {
            clientSocket.write(hackerResponse);
            clientSocket.end();
            return;
        }
        flaskSocket.write(request);
        denoSocket.write(request);
    })
        
    let flaskResponse = ""
    flaskSocket.on("data", (chunk) => {
        flaskResponse += chunk.toString();
    });
    let denoResponse = ""
    denoSocket.on("data", (chunk) => {
        denoResponse += chunk.toString();
    });

    let didFlaskEnd = false;
    let didDenoEnd = false
    flaskSocket.on("end", () => {
        didFlaskEnd = true;
        if(didDenoEnd) end();
    });
    denoSocket.on("end", () => {
        didDenoEnd = true;
        if(didFlaskEnd) end();
    });
    setTimeout(end, 1000)
});

server.listen(4000, () => {
    console.log("Proxy server is running on port 4000");
});
