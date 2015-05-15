from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    name= ndb.StringProperty()


    mail= ndb.StringProperty()


    text= ndb.TextProperty()

    created = ndb.DateTimeProperty(auto_now_add=True)
