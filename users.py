from sqlalchemy.dialects.postgresql import UUID
import uuid

from db import db

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # doesn't need to be in the def __init__ cause it already gets the UUID from the database
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String())
    email = db.Column(db.String())
    phone = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    active = db.Column(db.Boolean(), nullable=False, default=True)
    # org_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.org_id'))

    def __init__(self,first_name, last_name, email, phone, city, state, active=True):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.city = city
        self.state = state
        self.active = active

        super().__init__()

# CREATE TABLE IF NOT EXISTS users(
#     user_id SERIAL PRIMARY KEY,

#     org_id INT