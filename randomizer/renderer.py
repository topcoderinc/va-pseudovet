import types

import jinja2 

import custom_filters

'''
Wrapper for jinja2 templating engine
See http://jinja.pocoo.org/docs/2.10 for more details on the Jinja engine
'''
class Renderer:

	def __init__(self):
		'''
		Initialize class instance by loading template and custom filters 
		'''
		self.template_filename = 'continuity_of_care_document.xml'

		self.environment = jinja2.Environment(loader = jinja2.FileSystemLoader('./templates'))

		# load filters defined in custom_filters
		for a in dir(custom_filters):
			if isinstance(custom_filters.__dict__.get(a), types.FunctionType):
				self.environment.filters[a] = custom_filters.__dict__.get(a)

		self.template = self.environment.get_template(self.template_filename)

	def render(self, context):
		return self.template.render(context)
