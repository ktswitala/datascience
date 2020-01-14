
from .common import *

class WebServer(object):
	def __init__(self, redis):
		self.redis = redis

		self.flask_app = flask.Flask("league")
		self.flask_app.use_reloader=False

		self.flask_app.add_url_rule('/<path:path>', 'get_path', self.get_path)

		self.flask_thread = threading.Thread(target=self.run_flask)
		self.flask_thread.start()

	def get_path(self, path):

	def run_flask(self):
		self.flask_app.run(host='127.0.0.1', port=12222)
