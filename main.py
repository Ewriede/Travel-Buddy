import sqlalchemy as sa
import sqlalchemy.orm as so
import requests

from app import app, db
from app.models import User, Travelplan, Activities, Destination


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User,
            'Travelplan': Travelplan, 'Destination': Destination, 'Activities': Activities}
