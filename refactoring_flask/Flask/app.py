import logging
from Flask.py.utils import *
from Flask.routes import *
from logging.handlers import RotatingFileHandler
from Flask.py.apis import *
from Flask.db.pymongodb import *

if __name__ == "__main__":
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('showUserProfile.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(debug=True, host="0.0.0.0", port=5002)
