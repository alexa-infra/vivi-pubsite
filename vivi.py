import os
import re
import shutil
from datetime import datetime, date
from jinja2 import FileSystemLoader, Environment
from template.templatetags import templatetags
from template.templatefunctions import functions
from template.templatefilters import filters
from template.skipblockext import SkipBlockExtension
from urllib.parse import urlparse, urljoin
import sjson

ROOT_PATH = '.'

def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

class Config:
    def __init__(self):
        import local_config
        self.exclude = getattr(local_config, 'EXCLUDE', [])
        self.exclude = [re.compile(t) for t in self.exclude]
        self.rules = getattr(local_config, 'RULES', ())
        self.rules = [(re.compile(t[0]), t[1]) \
                for t in self.rules]
        self.url = getattr(local_config, 'URL', '/')
        self.title = getattr(local_config, 'TITLE', 'alexadotlife')
        self.author = getattr(local_config, 'AUTHOR', '')

class BaseEntry:
    def __init__(self, site, path, url):
        self.path = path
        self.url = url
        self.site = site
        self.settings = {}

    def get_dest(self):
        return os.path.join(self.site.dest, self.url)

    def render_meta(self):
        pass

    def patch(self):
        pass

    def is_static(self):
        pass

    def __getitem__(self, name):
        return self.settings[name]

    def __getattr__(self, name):
        try:
            return self.settings[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.path)

class Entry(BaseEntry):
    def get_template(self):
        template = self.site.env.get_template(self.path)
        template.globals['entry'] = self
        return template

    def render(self):
        dest = self.get_dest()
        makedirs(os.path.dirname(dest))
        with open(dest, 'w', encoding='utf8') as f:
            tmpl = self.get_template()
            text = tmpl.render()
            #text = text.encode('utf-8')
            f.write(text)

    def render_meta(self):
        tmpl = self.get_template()
        if 'meta' in tmpl.blocks:
            lines = []
            for line in tmpl.blocks['meta'](tmpl.new_context()):
                lines.append(line.strip())
            text = '\n'.join(lines)
            settings = sjson.loads(text)
            self.settings.update(settings)
            self.patch()
        if 'post_content' in tmpl.blocks:
            lines = []
            for line in tmpl.blocks['post_content'](tmpl.new_context()):
                lines.append(line)
            text = '\n'.join(lines)
            self.body = text

    def patch(self):
        if 'pub-date' not in self.settings:
            names = ['day', 'month', 'year']
            if all([t in self.settings for t in names]):
                day, month, year = [int(self.settings[t]) for t in names]
                dt = date(year, month, day)
            else:
                dt = date.today()
        else:
            dt = datetime.strptime(self.settings['pub-date'], '%Y-%m-%d')
        self.settings['date'] = dt
        if 'filename' in self.settings:
            self.settings['slug'] = self.settings['filename']
        else:
            _, filename = os.path.split(self.path)
            if not filename:
                filename = 'index'
            filename, _ = os.path.splitext(self.path)
            self.settings['slug'] = filename
    
    def is_static(self):
        return False

    @property
    def children(self):
        allpages = [entry for entry in self.site.entries if not entry.is_static()]
        base = os.path.dirname(self.url)
        childrenpages = [entry for entry in allpages if
                entry.url.startswith(base) and entry.url != self.url]
        childrenpages = sorted(childrenpages, key=lambda x: x.date,
                reverse=True)
        return childrenpages

    def get_url(self):
        url = self.url.endswith('index.html') and self.url[:-10] or self.url
        absurl = urljoin(self.site.url, url)
        return urlparse(absurl).path

    def get_absolute_url(self):
        url = self.url.endswith('index.html') and self.url[:-10] or self.url
        return urljoin(self.site.url, url)

class StaticEntry(BaseEntry):
    def render(self):
        dest = self.get_dest()
        makedirs(os.path.dirname(dest))
        shutil.copy2(self.path, dest)

    def is_static(self):
        return True

class Site:
    def __init__(self):
        self.cfg = Config()
        self.url = self.cfg.url
        self.title = self.cfg.title
        self.author = self.cfg.author
        self.loader = FileSystemLoader(ROOT_PATH)
        self.env = Environment(loader=self.loader)
        for ttag in templatetags:
            self.env.add_extension(ttag)
        self.env.add_extension(SkipBlockExtension)
        for tfunc in functions:
            self.env.globals[tfunc.__name__] = tfunc
        for tfilter in filters:
            self.env.filters[tfilter.__name__] = tfilter

        self.env.globals['site'] = self
        self.entries = []
        self.url_lookup = {}
        self.url_loopup_reverse = {}
        self.dest = os.path.join(os.path.abspath(ROOT_PATH), '_build')

    def exclude_path(self, path):
        for exc in self.cfg.exclude:
            if exc.search(path):
                return True
        return False

    def process_path(self, path):
        for rule, repl in self.cfg.rules:
            match = rule.match(path)
            if match:
                return rule.sub(repl, path), match
        return path, None

    def traverse(self):
        for root, _, files in os.walk(ROOT_PATH):
            for f in files:
                path = os.path.join(root, f)
                path = os.path.relpath(path, ROOT_PATH)

                if self.exclude_path(path):
                    continue

                url, match = self.process_path(path)
                print(path, '->', url)

                self.add_page(path, url, match)

    def add_page(self, path, url, match):
        entryclass = match and Entry or StaticEntry
        entry = entryclass(self, path, url)
        self.entries.append(entry)
        self.url_lookup[path] = entry
        self.url_loopup_reverse[url] = entry
        if match:
            url_settings = match.groupdict()
            entry.settings.update(url_settings)
        return entry

    @property
    def posts(self):
        posts = [p for p in self.entries if p.path == 'blog/index.html']
        if not posts:
            return None
        return posts[0].children

    def render_meta(self):
        for entry in self.entries:
            entry.patch()
        for entry in self.entries:
            print('Render meta', entry)
            entry.render_meta()

    def render(self):
        self.env.cache.clear()
        self.env.skip_blocks.append('meta')
        for entry in self.entries:
            print('Render', entry)
            entry.render()

if __name__ == "__main__":
    theSite = Site()
    theSite.traverse()
    theSite.render_meta()
    theSite.render()


