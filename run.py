from FlaskServer import app
import logging
from logging.handlers import RotatingFileHandler
import os

if __name__ == "__main__":
	app.secret_key = os.urandom(24)
	#app.run(debug=True, host="0.0.0.0", port=5001)
	formatter = logging.Formatter(
		"[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
	handler = RotatingFileHandler('showUserProfile.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	handler.setFormatter(formatter)
	app.logger.addHandler(handler)
	app.run(debug=True, host="0.0.0.0", port=5001)
