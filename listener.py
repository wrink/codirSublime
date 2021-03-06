import sublime, sublime_plugin
import os
from . import history, file_listener
from . import codir_client as client

class CodirListener(sublime_plugin.EventListener):
	def on_modified_async(self, view):
		is_delta = history.is_delta(view)
		if view.window() and view.window().id() in client.sockets and not is_delta and view.file_name():
			history.buffer_history[view.id()].append(view.substr(sublime.Region(0, view.size())))

			socket = client.sockets[view.window().id()]
			deltas = history.get_deltas(view)

			path = 'codirSublime/projects/'
			file = view.file_name()
			if file.index(path) > 0 and (deltas['additions'] != {} or deltas['removals'] != {}):
				history.delta_history[view.id()].append(deltas)
				history.history_pointer[view.id()] = len(history.delta_history[view.id()]) - 1
				print (history.history_pointer[view.id()])

				path_start = file.index(path) + len(path + socket['shareid'] + '/')
				socket['socket'].emit('workspace-file-edit-update', {'path': file[path_start:], 'deltas': deltas, 'shareid': socket['shareid']})

	def on_text_command(self, view, command_name, args):
		if command_name == 'undo' and view.window() and view.window().id() in client.sockets:
			return ('codir_undo')

	def on_load(self, view):
		print('loaded')
		id = view.window().id()
		if id in client.sockets:
			history.init_view(view)
			print('test')
			socket = client.sockets[view.window().id()]
			dir = os.path.dirname(os.path.abspath(__file__)) + '/projects/' + socket['shareid'] + '/'
			filename = view.file_name()
			if dir in filename:
				sub_path = filename[filename.index(dir) + len(dir):]
				event = {'shareid': socket['shareid'], 'path': sub_path}
				socket['socket'].emit('workspace-open-file-update', event)

	def on_new(self, view):
		id = view.window().id()
		if id in client.sockets:
			print ('new view')
			history.init_view(view)
		

	def on_clone(self, view):
		id = view.window().id()
		if id in client.sockets:
			print ('cloned view')
			history.init_view(view)