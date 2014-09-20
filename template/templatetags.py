from jinja2 import nodes
from jinja2.ext import Extension
import sjson

class MetaInfoExtension(Extension):
    tags = set(['meta'])

    def parse(self, parser):
        lineno = parser.stream.__next__().lineno

        meta = parser.parse_statements(['name:endmeta'], drop_needle=True)
        try:
            config = meta[0].nodes[0].data
        except IndexError:
            config = ''

        args = [nodes.Name('entry', 'load'), nodes.Const(config)]
        return nodes.CallBlock(self.call_method('_config', args=args),
                [], [], '').set_lineno(lineno)

    def _config(self, entry, config, caller):
        if 'render_meta' in self.environment.globals:
            settings = sjson.loads(config)
            entry.settings.update(settings)
        return ''

templatetags = [MetaInfoExtension]
