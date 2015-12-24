import sublime, sublime_plugin
import threading, re, zipfile
import sys, os
from . import history
path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path + '/socketIO')
from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

global sockets

sockets = {}

class CodirClientCommand(sublime_plugin.WindowCommand):
	def run(self):		
		self.window.show_input_panel('ShareID', 'localhost:8000', self.verify_shareid, None, None)

	def verify_shareid(self, shareid):
		if re.match(r'((^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(localhost)):\d{1,4}$', shareid):
			t = ClientThread(shareid)
			t.start()
		else:
	 		sublime.error_message('ERROR: ' + shareid + 'is not a valid ShareID')

class ClientThread(threading.Thread):
	def __init__(self, shareid):
		self.shareid = shareid
		threading.Thread.__init__(self)
		
	def run(self):
		sublime.run_command('new_window')
		self.window = sublime.active_window()

		host, port = self.shareid.split(':')
		print ('test0')
		self.socket = SocketIO(host, int(port), LoggingNamespace)
		print ('test1')
		
		self.socket.on('live-file-connection', self.download)

		self.socket.on('workspace-file-edit-update', self.apply)

		self.socket.on('workspace-open-file-update', self.apply_all)
		print ('test2')
		self.socket.emit('live-file-connection', '')
		while True:
			self.socket.wait(seconds=1)

	def download(self, file):
		print ('start')
		self.shareid = file['shareid']
		sockets[self.window.id()] = {'socket': self.socket, 'window': self.window, 'shareid': self.shareid}

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects')

		fp = os.path.relpath(path + '/projects')
		print (fp)

		f = open(fp + '/' + self.shareid + '.zip', 'wb+')
		f.write(bytes.fromhex(file['zip']))
		f.close()

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects/' + self.shareid)

		z = zipfile.ZipFile(path + '/projects/' + self.shareid + '.zip', 'r')
		z.extractall(path + '/projects/' + self.shareid + '/')
		z.close()
		
		self.window.set_project_data({'folders': [ {'path': path + '/projects/' + self.shareid + '/'} ] })
		print ('done')

	def apply(self, delta):
		path = os.path.dirname(os.path.realpath(__file__)) + '/projects/' + self.shareid + '/' + delta['path']

		views = self.window.views()
		for view in views:
			filename = view.file_name()
			if path in filename and filename.index(path) + len(path) == len(filename):
				view.run_command('apply_deltas', {'deltas': delta['deltas']})
				#history.delta_queue[view.id()].append(delta['deltas'])

	def apply_all(self, deltas):
		for delta in deltas['deltas']:
			path = os.path.dirname(os.path.realpath(__file__)) + '/projects/' + self.shareid + '/' + deltas['path']

			views = self.window.views()
			for view in views:
				filename = view.file_name()
				if path in filename and filename.index(path) + len(path) == len(filename):
					view.run_command('apply_deltas', {'deltas': delta})

	# def add_to_queue(self, *delta):
	# 	ids = []

	# 	for i, window in sublime.windows():
	# 		for j, view in window.views():
	# 			if delta[0]['filename']

	# 	history.delta_queue[id]