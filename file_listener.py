import sublime, sublime_plugin
import threading, os, time, zipfile, json, binascii
from . import codir_client as client
path = os.path.dirname(os.path.realpath(__file__))

global windows
windows = {}

class ProjectWatcher(threading.Thread):
	def __init__(self, window, shareid):
		self.shareid = shareid
		self.window = window
		self.socket = client.sockets[self.window.id()]
		self.project_data = window.project_data()['folders']
		self.contents = self.get_contents(self.project_data)
		self.incoming = False
		threading.Thread.__init__(self)
	
	def run(self):
		while 1:
			if not self.window.id() in windows: return
			before = self.contents
			self.project_data = self.window.project_data()['folders']
			after = self.get_contents(self.project_data)
			self.contents = after

			if before == after: continue

			added = [f for f in after if not f in before]
			removed = [f for f in before if not f in after]

			if not self.check_incoming():
				socket = client.sockets[self.window.id()]
				a_files = [f for f in added]
				r_files = [f for f in removed]

				add, rem = [], []
				for f in added:
					is_root = True
					for r in add:
						if r in f and f.index(r) == 0:
							is_root = False
							break
					if is_root:
						add.append(f)
				for f in removed:
					is_root = True
					for r in rem:
						if r in f and f.index(r) == 0:
							is_root = False
							break
					if is_root:
						rem.append(f)

		fp = os.relpath(path + '/projects/' + self.shareid + '/');

		z = zipfile.ZipFile(fp + '.fdeltas.zip', 'w')
		for f in add:
			z.write(os.path.relpath(f))

		fdeltas = {'added': {}, 'removed': {}}

		for f in add:
			if fp in f:
				index = f.index(path)
				fdeltas['added'][os.path.basename(f)] = f[index:]
			else:
				fdeltas['added'][os.path.basename(f)] = None
		for f in rem:
			index = f.index(path)
			fdeltas['removed'][f[index:]] = None
		
		f = open(fp + '.fdeltas.json', 'w')
		json.dump(fdeltas, f)
		f.close()
		z.write(os.path.relpath(fp + '.fdeltas.json'))
		z.close()

		z = open(fp + '.fdeltas.zip', 'rb')
		self.socket.emit('workspace-project-edit-update', binascii.hexlify(z.read()))
		z.close()

		time.sleep(10)




		# before = dict ([(f, None) for f in os.listdir (paths)])
		# while 1:
		# 	time.sleep (10)
		# 	after = dict ([(f, None) for f in os.listdir (paths)])
		# 	added = [f for f in after if not f in before]
		# 	removed = [f for f in before if not f in after]
		# 	if added: print "Added: ", ", ".join (added)
		# 	if removed: print "Removed: ", ", ".join (removed)
		# 	before = after

	def get_contents(self, folders):
		ret = []
		for folder in self.project_data:
			#print('get_contents of '+ folder['path'])
			ret.append(folder)
			for root, dirs, files in os.walk(folder['path']):
				ret+=[folder['path']+'/'+directory for directory in dirs]
				ret+=[folder['path']+'/'+f for f in files]
		return ret

	def check_incoming(self):
		if self.incoming:
			self.incoming = False
			return True
		return False