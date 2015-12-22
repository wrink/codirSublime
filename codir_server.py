import sublime, sublime_plugin
import socket, subprocess, random, threading, os, sys
from . import codirServer
# path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, path + '/js')
# from Naked.toolshed.shell import execute_js, muterun_js


class CodirShareCommand(sublime_plugin.WindowCommand):
	def run(self, paths, socket=random.randint(8000, 8999)):

		t = ServerThread(paths[0], socket, self.window)
		t.start()

class CodirShareToCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.paths = paths
		self.window.show_input_panel('Port', '8000', self.share, None, None)

	def share(self, port):
		self.window.run_command('codir_share', {'paths': self.paths, 'socket': port})

class ServerThread(threading.Thread):
	def __init__(self, path, socket, window):
		self.path = path
		self.socket = socket
		self.window = window
		threading.Thread.__init__(self)

	def run(self):
		#out = self.window.create_output_panel('shareid')
		ip = socket.gethostbyname(socket.gethostname())
		print(os.path.relpath(os.path.dirname(os.path.abspath(__file__))))
		filepath = os.path.relpath(os.path.dirname(os.path.abspath(__file__))) + '/codirServer/index.js'
		filepath = filepath.replace(' ', '\ ')
		#filepath = 'codirServer/index.js'
		path = self.path.replace(' ', '\ ')
		sublime.error_message('Shareid: ' + ip + ':' + str(self.socket))
		#out.run_command('insert', [0, 'Shareid: ' + ip + ':' + str(self.socket)])
		#self.window.view().focus_view(out)
		#print('node '+ filepath + ' run ' + os.path.relpath(path) + ' -p ' + self.socket + ' &')
		#print(execute_js(filepath, 'run ' + os.path.relpath(path) + ' -p ' + self.socket + ' &'))
		#p.wait()
		codirServer.run(path, str(self.socket))
		print('done')
		#subprocess.call(['node', '/codirServer/index.js'), 'run', self.path, '-p', self.socket], shell=True)
