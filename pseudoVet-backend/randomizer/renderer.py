import types

import jinja2

from randomizer import custom_filters
from config import TEMPLATES_DIR

'''
Wrapper for Jinja2 templating engine
See http://jinja.pocoo.org/docs/2.10 for more details on the Jinja engine
'''


class Renderer:
    def __init__(self):
        """
        Initialize class instance by loading template and custom filters
        """
        self.template_filename = 'continuity_of_care_document.xml'

        self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))

        # load filters defined in custom_filters
        for a in dir(custom_filters):
            if isinstance(custom_filters.__dict__.get(a), types.FunctionType):
                self.environment.filters[a] = custom_filters.__dict__.get(a)

        self.template = self.environment.get_template(self.template_filename)

    def render(self, context):
        """
        Render template using the provided context
        """
        return self.template.render(context)
