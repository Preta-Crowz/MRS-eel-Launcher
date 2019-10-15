#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import http.server
import socketserver
import socket
 
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
     """
     New features w/r to BaseHTTPServer.HTTPServer:
     - serves multiple requests simultaneously
     - catches socket. timeout and socket.error exceptions (raised from
       RequestHandler)
     """
     
     def __init__(self, *args):
          http.server.HTTPServer.__init__(self, *args)
          
     def process_request_thread(self, request, client_address):
          """
          Overrides SocketServer.ThreadingMixIn.process_request_thread
          in order to catch socket.timeout
          """
          try:
               self.finish_request(request, client_address)
               self.close_request(request)
          except socket.timeout:
               print('Timeout during processing of request from', end=' ')
               print(client_address)
          except socket.error as e:
               print(e, 'during processing of request from', end=' ')
               print(client_address)
          except:
               self.handle_error(request, client_address)
               self.close_request(request)
 
class TimeoutHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
     """
     Abandon request handling when client has not responded for a
     certain time. This raises a socket.timeout exception.
     """
 
     # Class-wide value for socket timeout
     timeout = 3 * 60
     
     def setup(self):
          'Sets a timeout on the socket'
          self.request.settimeout(self.timeout)
          http.server.SimpleHTTPRequestHandler.setup(self)
 
def main():
     try:
          http.server.test(TimeoutHTTPRequestHandler, ThreadedHTTPServer)
     except KeyboardInterrupt:
          print('^C receved, shutting down server')
 
if __name__ == '__main__':
     main()