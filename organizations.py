from sqlalchemy.dialects.postgresql import UUID
import uuid 

from db import db


#     CREATE TABLE IF NOT EXISTS organizations (
#         org_ig SERIAL PRIMARY KEY,
#         name VARCHAR NOT NULL,
#         phone VARCHAR,
#         city VARCHAR,
#         state VARCHAR,
#         active VARCHAR NOT NULL DEFAULT True,
#         type VARCHAR

class Organization(db.Model):
    __tablename__ = 'organizations'
    org_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nulable=False)
    phone =  db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    type = db.Column(db.String())
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, name, phone, city, state, type, active=True):
        self.name = name
        self.phone = phone
        self.city = city
        self.state = state
        self.type = type
        self.active = active

