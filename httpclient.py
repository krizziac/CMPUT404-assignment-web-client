#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Krizzia Concepcion
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
    def get_host_port_path(self,url):
        '''
        Method extracts the host, port, and path given the url. If no post is provided, we give it a default of port 8

        Resources used: 
        link: https://docs.python.org/3/library/urllib.parse.html
        license: Python Software Foundation License Version 2
        Used to figure out how to extract host, port, and path using urllib.parse

        link: https://www.techopedia.com/definition/15709/port-80#:~:text=This%20strategy%20began%20back%20in,protocol%20that%20uses%20port%20443.
        Author: Jennifer Seaton (March 11, 2022)
        Used to find out what port number to give, if there was none provided
        '''
        host = urllib.parse.urlparse(url).hostname
        port= urllib.parse.urlparse(url).port
        path = urllib.parse.urlparse(url).path

        if path == "":
            path  = "/"

        if port is None:
            port = 80 #default port number
        
        return host, port,path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        
        full_request = data.split(" ")
        code = full_request[1]
        
        return int(code)

    #method get_headers was not used
    def get_headers(self,data):
        return None
    
    def get_body(self, data):
        '''
        Function returns the body returned by the http request
        
        Resouce Used:
        Title: How do I get the body of a http response from a string containing the entire response, in Python?
        Link: https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res
        Posted by: sorin (https://stackoverflow.com/users/99834/sorin)
        Answer used: bogdan (https://stackoverflow.com/users/192632/bogdan)
        Date Published: Dec 12, 2011
        License: CC BY-SA 3.0.

        Used the code to retrieve the body of the http response and print it to stdout.
        '''
        body  = data.find('\r\n\r\n')
        if body >= 0 :
            return data[body+4:]
        return body
     
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
        '''
        Sends a GET request and prints out the http response. 
        
        Resource used:
        Title: Add params to given URL in Python
        Link:https://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python
        Posted by: z4y4ts (https://stackoverflow.com/users/231412/z4y4ts)
        Answer used: Łukasz (https://stackoverflow.com/users/4999/https://stackoverflow.com/users/231412/z4y4ts)
        Date published: March 24, 2010
        License: CC BY-SA 2.5.

        Used the code to encode the args then add it to the query parameters (if there are no query paramters in the url, but a query was made, 
        the code will encode the query, then add the query into the url)
        '''
        code = 500
        body = ""
        

        #Check if there are args/queries
        #resource listed above was used here
        if args != None and urllib.parse.urlparse(url).query == '' : # there is a query but it's not in the url
            if type(args) == dict: #encode the args
                url_p = list(urllib.parse.urlparse(url))
                query = urllib.parse.urlencode(args)
                url_p[4] = query
                url = urllib.parse.urlunparse(url_p) #update the url with the query in the host name
        
        host,port,path= self.get_host_port_path(url)    
        connect_socket = self.connect(host,port)
    

        get_req = "GET {0} HTTP/1.1\r\n".format(path) 
        get_req = get_req+  "Host: {0}\r\n".format(host)
        get_req = get_req +"Connection: close\r\n\r\n"


        
        self.sendall(get_req)
        reply = self.recvall(connect_socket)

        code = self.get_code(reply)
        body = self.get_body(reply)
       
        print(reply) #print to stdout
        self.close()
       
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        '''
        Sends a POST request with encoded args

        Resource Used: 
        Title: How to URL encode in Python 3?
        Link: https://stackoverflow.com/questions/40557606/how-to-url-encode-in-python-3
        Posted By: amphibient (https://stackoverflow.com/users/1312080/amphibient)
        Answer used: Adam Smith (https://stackoverflow.com/users/3058609/adam-smith)
        Date Published: Nov 11, 2016
        License: CC BY-SA 3.0

        Used to figure out how to encode args in order to send it with the http response
        
        '''
        code = 500
        body = ''
      
        host,port,path= self.get_host_port_path(url)
        connect_socket = self.connect(host,port)

        #resource linked above was used here
        if args == None:
            content_size = 0
        elif type(args) == dict:
            args = urllib.parse.urlencode(args)
            content_size = len(args)

       
        post_req = "POST {0} HTTP/1.1\r\nHost:{1}\r\nContent-Length:{2}\r\n".format(path,host,content_size)
        post_req = post_req + "Content-Type: application/x-www-form-urlencoded\r\n"
        post_req = post_req + "Connection: close\r\n\r\n"
        post_req = post_req + "{0}\r\n".format(args)

        self.sendall(post_req)
        reply = self.recvall(connect_socket)
        code = self.get_code(reply)
        body = self.get_body(reply)

       
        print(reply)
        self.close()

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
        print(client.command( sys.argv[2], sys.argv[1]  ))
    else:
        print(client.command( sys.argv[1] ))
    

   
   