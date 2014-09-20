GLOBALS = {
        "title": "",
        "author": ""
}

RULES = (
    (r"(?P<filepath>.*)index\.html", "\g<filepath>index.html"),
    (r"(?P<filepath>.*)(?P<year>\d{4})/(?P<month>\d{2})-(?P<day>\d{2})-(?P<filename>.*)\.html", "\g<filepath>\g<year>/\g<month>/\g<day>/\g<filename>/index.html"),
    (r"(?P<filename>.*)\.html", "\g<filename>/index.html"),
    (r"sitemap.xml", "sitemap.xml"),
#    (r"(.*)", "\g<1>")
)

EXCLUDE = [
        r"^local/",
        r"^_build/",
        r"config\.sjson",
        r"\.py$",
        r"\.pyc$",
        r"^\.hg",
        r"\.swp$",
        r"_[^\.]*\.html$",
        r"^requirements.txt$",
]

URL = "http://192.168.1.68:8001/"
