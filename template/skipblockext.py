from jinja2.ext import Extension

class SkipBlockExtension(Extension):
    def __init__(self, environment):
        super(SkipBlockExtension, self).__init__(environment)
        environment.extend(skip_blocks=[])

    def filter_stream(self, stream):
        block_level = 0
        skip_level = 0
        in_endblock = False

        for token in stream:
            if token.type == 'block_begin':
                if stream.current.value == 'block':
                    block_level += 1
                    if stream.look().value in self.environment.skip_blocks:
                        skip_level = block_level

            if token.value == 'endblock':
                in_endblock = True

            if skip_level == 0:
                yield token

            if token.type == 'block_end':
                if in_endblock:
                    in_endblock = False
                    block_level -= 1

                    if skip_level == block_level+1:
                        skip_level = 0
