#alexapi/AVS/interface_manager.py

import os

import alexapi.shared as shared
from alexapi.avs.directive_dispatcher import DirectiveDispatcher
from alexapi.http.http import Http

class InterfaceManager:
	__directive_path = None
	__avs_session = None
	__directive_dispatcher = None

	class Payload:
		filename = None
		json = None

	def __init__(self):
		self.__avs_session = Http(self)
		self.__directive_dispatcher = DirectiveDispatcher(self)
		self.__import_modules()

	def __check_if_not_error(self, response):
		if not response.status_code >= 200 and not response.status_code < 300:
			print("{}(process_response Error){} Status Code: {} - {}".format(shared.bcolors.WARNING, shared.bcolors.ENDC, response.status_code, response.text))
			return False

		return True

	def __import_modules(self):
		module_root = 'alexapi.avs'
		interface_dir = 'Interface'

		print
		print '----------------------'
		for module in os.listdir(os.path.dirname(__file__) + '/%s/' % interface_dir):
			if module == '__init__.py' or module[-3:] != '.py':
				continue

			module = '{}.{}.{}'.format(module_root, interface_dir, module.strip('.py'))
			print 'Importing ' + module + '...'
			__import__(module, locals(), globals())

		print '----------------------'
		print

		del module
		import Interface #TODO: make dynamic

		for module in [x for x in dir(locals()[interface_dir]) if not x.startswith('__') and not x == 'os']:
			modname = locals()['module'] # Get interface name
			mod = getattr(Interface, locals()['module'], False)
			interface = getattr(mod, locals()['module'], False)(self)
			setattr(self, modname, interface)

	def get_avs_session(self):
		return self.__avs_session.get_avs_session()

	def send_event(self, namespace, event_name):
		print "Dispatching event: {}...".format(namespace)
		class_instance = getattr(self, str(namespace), None)
		if class_instance:
			event_method = getattr(class_instance, str(event_name), None)
			self.process_directive(event_method())
		else:
			print "Unknown event(namespace/name): {}/{}...".format(namespace, event_name)
			return False

	def dispatch_directive(self, payload=False):
		namespace = payload.json['directive']['header']['namespace']
		directive_name = payload.json['directive']['header']['name']

		class_instance = getattr(self, str(namespace), None)

		if class_instance:
			print "Dispatching directive(namespace/name): {}/{}...".format(namespace, directive_name)
			directive_method = getattr(class_instance, str(directive_name), None)
			directive_method(payload)
		else:
			print "Unknown directive(namespace/name): {}/{}...".format(namespace, directive_name)
			return False

	def process_directive(self, response):
		print "Processing directive..."
		self.__directive_dispatcher.processor(response)
