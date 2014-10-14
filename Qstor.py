import os
import sys
import cgi
import json
import shutil
import hashlib
import SocketServer

from sys import argv
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

tmpDir = "/tmp/qstor"
try:	os.makedirs(tmpDir)
except:	pass
os.chdir(tmpDir)



class Transporter(BaseHTTPRequestHandler):
	def headerText(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def headerFile(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/octet-stream')
		self.end_headers()

	def do_GET(self):
		filename = self.path.lstrip("/")		
		if os.path.isfile(filename):
			self.headerFile()
			with open(filename,"r") as f:
				self.wfile.write(f.read())
		else:
			self.headerText()
			self.wfile.write(json.dumps({"error":"nonefound"},sort_keys=False,indent=4))

	def do_HEAD(self):
		self.headerText()
	
	def do_POST(self):
		form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
		filename = self.path.lstrip("/")
		print("\t[R] Wrote '%s' to file"%(filename))
		filenametemp = filename+".incoming"
		try:
			ttl = form['ttl'].file.read()
			print("\t[R] Setting TTL for '%s' to %s Seconds"%(filename,ttl))
		except:pass
		data = form['file'].file.read()
		open(filenametemp, "wb").write(data)
		shutil.move(filenametemp,filename)
		print("\t[R] Calculating hashsum for '%s'"%(filename))
		filehash = hashlib.md5(open(filename,'rb').read()).hexdigest()
		doneData = { "info":"done", "md5":filehash }
		outputJson = json.dumps(doneData,sort_keys=False,indent=4)
		outputJson = json.dumps(doneData)
		self.wfile.write(outputJson)
		#'''
	
def publicInterface(server_class=HTTPServer, handler_class=Transporter, port=651):
	server_address = ('', port)
	httpProc = server_class(server_address, handler_class)
	print('\t[I]\tStarting server')
	httpProc.serve_forever()


if __name__ == "__main__":
  publicInterface()
