import jinja2

#def sourcecode(value, lang='', linenos=False):
#    try:
#        from pygments import highlight
#        from pygments.lexers import get_lexer_by_name, TextLexer
#        from pygments.formatters import HtmlFormatter
#    except ImportError:
#        raise jinja2.TemplateError('pygments is not installed')
#
#    VARIANTS = {
#        'default': HtmlFormatter(noclasses=False),
#        'linenos': HtmlFormatter(noclasses=False, linenos=True),
#    }
#    try:
#        lexer = get_lexer_by_name(lang)
#    except ValueError:
#        lexer = TextLexer()
#    variant = linenos and 'linenos' or 'default'
#    formatter = VARIANTS[variant]
#    parsed = highlight(value, lexer, formatter)
#    #parsed = parsed.replace("==", "&#61;&#61;")
#    return jinja2.Markup(parsed)
def sourcecode(value, lang=''):
    m = jinja2.Markup('<pre class="prettyprint lang-%s">%s</pre>')
    return m % (lang, value)

def markdown(value):
    try:
        from markdown import Markdown
        md = Markdown(extensions=['footnotes'])
    except ImportError:
        try:
            from markdown2 import Markdown
            md = Markdown(extras=['footnotes', 'code-friendly'])
        except ImportError:
            raise jinja2.TemplateError('Markdown is not installed!')

    return jinja2.Markup(md.convert(value))

def textile(value):
    try:
        import textile
    except ImportError:
        raise jinja2.TemplateError('textile is not installed!')

    return jinja2.Markup(textile.textile(value))

def rfc3339(date):
    tz = date.strftime('%Z') or 'Z'
    return date.isoformat() + tz

filters = [markdown, textile, sourcecode, rfc3339]
