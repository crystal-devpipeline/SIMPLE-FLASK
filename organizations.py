from sqlalchemy.dialects.postgresql import UUID
import uuid 

from db import db
import marshmallow as ma
# from users import UsersSchema


#     CREATE TABLE IF NOT EXISTS organizations (
#         org_ig SERIAL PRIMARY KEY,
#         name VARCHAR NOT NULL,
#         phone VARCHAR,
#         city VARCHAR,
#         state VARCHAR,
#         active VARCHAR NOT NULL DEFAULT True,
#         type VARCHAR

class Organizations(db.Model):
    __tablename__ = 'organizations'
    org_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #genreates a unique ifentifier
    name = db.Column(db.String(), nullable=False, unique=True)
    phone =  db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    active = db.Column(db.Boolean, nullable=False, default=True)
    type = db.Column(db.String())

    users = db.relationship('Users', back_populates='organization')

    def __init__(self, name, phone, city, state, type, active=True):
        self.name = name
        self.phone = phone
        self.city = city
        self.state = state
        self.type = type
        self.active = active

class OrganizationsSchema(ma.Schema):
    class Meta:
        fields = ('org_id', 'name', 'phone', 'city','state', 'active', 'type', 'users')
    users = ma.fields.Nested('UsersSchema', only=['user_id', 'first_name', 'last_name','organization'], many=True)
org_schema = OrganizationsSchema()
orgs_schema = OrganizationsSchema(many=True)

class PublicOrganizationsSchema(ma.Schema):
    class Meta:
        fields = ('name', 'city', 'state')

public_org_schema = PublicOrganizationsSchema()
public_orgs_schema = PublicOrganizationsSchema(many=True)

# get a org id and add it to the user add in postman 