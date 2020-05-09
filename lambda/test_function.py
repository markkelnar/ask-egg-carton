import logging

from .secret import SecretThing
from .db import DatabaseThing


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    secrets = SecretThing()
    secret = secrets.get_secret()