#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # parse the url
        parsed = urllib.parse.urlparse(url)
        # get host name, port, and path
        hostname = parsed.hostname
        port = parsed.port
        path = parsed.path

        if port == None:
            port = 80
        if not path.endswith('/'):
            path += '/'

        return hostname, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Return status code as int from the data
        return int(data.split()[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        # split the body from the data and return
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port(url)
        # connect to host:port
        self.connect(host, port)
        # send a GET request through the connection with specified path and host
        self.sendall(f"""GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Charset: utf-8\r\nConnection: close\r\n\r\n""")
        # receive data from the request
        data = self.recvall(self.socket)
        # get status code from the data
        code = self.get_code(data)
        # get the body from the data
        body = self.get_body(data)
        # close connection
        self.close()
        # Output status code and body
        print('Code:{code}\nBody:{body}\n'.format(code=code,body=body))

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port(url)

        if args == None:
            content = ''
            content_length = 0
        else:
            content = urllib.parse.urlencode(args)
            content_length = len(content)

        # connect to host:port
        self.connect(host, port)
        # Send POST request through connection with specified path and host
        self.sendall(f"""POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Charset: utf-8\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{content}""")
        # Receive data returned from the socket
        data = self.recvall(self.socket)
        # Get status code from data
        code = self.get_code(data)
        # Get body from data
        body = self.get_body(data)
        # Close the connection
        self.close()

        # output status code and body
        print('Code:{code}\nBody:{body}\n'.format(code=code,body=body))

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
