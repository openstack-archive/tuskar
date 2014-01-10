import logging

# There is probably a better way of doing this, but it was being done
# in the models.py while I was cleaning that up. I suspect this will
# be moved elsewhere in the future.

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
