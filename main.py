#!/usr/bin/env python
import hashlib
import hmac
import os
import datetime
import time
import uuid

import jinja2
import webapp2
from models import Sporocilo
from models import Uporabnik
from secret import secret


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

        cookie_value = self.request.cookies.get("uid")

        if cookie_value:
            params["logiran"] = self.preveri_cookie(cookie_vrednost=cookie_value)
        else:
            params["logiran"] = False

        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))

    def ustvari_cookie(self, uporabnik):
        uporabnik_id = uporabnik.key.id()
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        expires_ts = int(time.mktime(expires.timetuple()))
        sifra = hmac.new(str(uporabnik_id), str(secret) + str(expires_ts), hashlib.sha1).hexdigest()
        vrednost = "{0}:{1}:{2}".format(uporabnik_id, sifra, expires_ts)
        self.response.set_cookie(key="uid", value=vrednost, expires=expires)

    def preveri_cookie(self, cookie_vrednost):
        uporabnik_id, sifra, expires_ts = cookie_vrednost.split(":")

        if datetime.datetime.utcfromtimestamp(float(expires_ts)) > datetime.datetime.now():
            preverba = hmac.new(str(uporabnik_id), str(secret) + str(expires_ts), hashlib.sha1).hexdigest()

            if sifra == preverba:
                return True
            else:
                return False
        else:
            return False

class MainHandler(BaseHandler):
    def get(self):
        self.render_template("hello.html")

class RezultatHandler(BaseHandler):
    def post(self):

        name = self.request.get("name")
        mail = self.request.get("mail")
        text = self.request.get("text")

        sporocilo = Sporocilo(name=name, mail=mail, text=text)
        sporocilo.put()

        self.render_template("rezultat.html")

class SeznamHandler(BaseHandler):
    def get(self):
        seznam = Sporocilo.query(Sporocilo.izbrisan == False).fetch()

        params = {"seznam": seznam}

        self.render_template("seznam.html", params=params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        self.render_template("posamezno_sporocilo.html", params=params)

class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        self.render_template("uredi.html", params=params)

    def post(self, sporocilo_id):

        novi_vnos = self.request.get("novime")
        novi_vnos2 = self.request.get("novmail")
        novi_vnos3 = self.request.get("novtext")

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        sporocilo.name = novi_vnos
        sporocilo.mail = novi_vnos2
        sporocilo.text = novi_vnos3

        sporocilo.put()

        self.redirect_to("seznam")

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}

        self.render_template("izbrisi.html", params=params)

    def post(self, sporocilo_id):

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.izbrisan = True
        sporocilo.put()

        self.redirect_to("seznam")
class RegistracijaHandler(BaseHandler):
    def get(self):
        self.render_template("registracija.html")
    def post(self):
        ime = self.request.get("ime")
        priimek = self.request.get("priimek")
        email = self.request.get("email")
        geslo = self.request.get("geslo")
        ponovno_geslo = self.request.get("ponovno_geslo")

        if geslo == ponovno_geslo:
            Uporabnik.ustvari(ime=ime, priimek=priimek, email=email, original_geslo=geslo)
            return self.redirect_to("main")

class LoginHandler(BaseHandler):
    def get(self):
        self.render_template("login.html")
    def post(self):

        email = self.request.get("email")
        geslo = self.request.get("geslo")

        uporabnik = Uporabnik.query(Uporabnik.email == email).get()

        if Uporabnik.preveri_geslo(original_geslo=geslo, uporabnik=uporabnik):
            self.ustvari_cookie(uporabnik=uporabnik)
            self.redirect_to("main")
            return
        else:
            self.write("NO NO :(")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', SeznamHandler, name="seznam"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
    webapp2.Route('/registracija', RegistracijaHandler),
    webapp2.Route('/login', LoginHandler),
], debug=True)
