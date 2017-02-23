import jinja2
import webapp2
import json
import os
from google.appengine.api import users
from google.appengine.api import urlfetch
from models import Message

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)



class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        user = users.get_current_user()
        params["user"] = user
        if user:
            logged_in = True
            logout_url = users.create_logout_url("/")
            params["logout_url"] = logout_url
        else:
            logged_in = False
            login_url = users.create_login_url(self.request.url)
            params["login_url"] = login_url
        params["logged_in"] = logged_in
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("main.html")

    def post(self):
        user = users.get_current_user()
        sender = user.email()
        receiver = self.request.get("receiver")
        subject = self.request.get("subject")
        text = self.request.get("text")
        if not receiver:
            return self.write("Please enter a user.")
        if "<script>" in text:
            return self.write("You shall not try to hack me! No Sir!")

        message = Message(sender=sender,receiver=receiver, subject=subject, text=text)
        message.put()
        return self.redirect_to("sent_messages")


class SentMessagesHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        messages = Message.query(Message.sender == user.email()).order(-Message.created).fetch()
        params = {"messages" : messages}
        return self.render_template("sent_messages.html", params)

class InboxHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        messages = Message.query(Message.receiver == user.email()).order(-Message.created).fetch()
        params = {"messages": messages}
        return self.render_template("inbox.html", params)

class MessageDeleteHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("message_delete.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.key.delete()
        return self.redirect_to("sent_messages")


class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=Puerto+Baquerizo+Moreno,at&lang=en&units=metric&appid=edad3650cccd627742ecbaaafca2ea9b"
        weather_info = json.loads(urlfetch.fetch(url).content)
        params = {"weather_info": weather_info}
        return self.render_template("weather.html", params=params)

class AboutHandler(BaseHandler):
    def get(self):
        return self.render_template("about.html")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/sent_messages', SentMessagesHandler, name="sent_messages"),
    webapp2.Route('/inbox', InboxHandler),
    webapp2.Route('/about', AboutHandler),
    webapp2.Route('/weather', WeatherHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', MessageDeleteHandler),
], debug=True)
