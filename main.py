#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Sporocilo



template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        self.render_template("hello.html")

class RezultatHandler(BaseHandler):
    def post(self):

        sporocilo = Sporocilo()
        sporocilo.name = self.request.get("name")
        sporocilo.mail = self.request.get("mail")
        sporocilo.text = self.request.get("text")

        sporocilo.put()

        self.render_template("rezultat.html")

class SeznamHandler(BaseHandler):
    def get(self):
        seznam = Sporocilo.query().fetch()

        params = {"seznam": seznam}

        self.render_template("seznam.html", params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        self.render_template("posamezno_sporocilo.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', SeznamHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
], debug=True)
