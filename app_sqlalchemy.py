from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from users import Users
from organizations import Organization
from db import db, init_db
import uuid

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "usermgt3"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_host}/{database_name}' #connection string to db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

def create_all():
    with app.app_context():
        db.create_all()
        

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False

def user_exists(user_id):
    if not user_id.isnumeric():
        return False

def org_exists(org_id):
    if not org_id.isnumeric():
        return False

def get_user_from_object(user):
    return{
        "user_id":user.user_id,
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email,
        "phone":user.phone,
        "city":user.city,
        "state":user.state,
        "active":user.active
    }

def get_org_from_object(organization):
    return{
        "name":organization.name,
        "phone":organization.phone,
        "city":organization.city,
        "state":organization.state,
        "type":organization.type,
        "active":organization.active,       
    }

#CREATE**************************************
@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json


    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email') #None
    if not email:
        return "Email must not be an empty str", 400
    phone = data.get('phone')
    if len(phone) > 20: 
        return "Your phone number should be under 20 characters", 400
    city = data.get('city')
    state= data.get('state')
    # org_id = data.get('org_id')

    new_user_record = Users(first_name, last_name, email, phone, city, state)
    db.session.add(new_user_record) # added from db.Model 
    db.session.commit()

    return "User added", 201



@app.route('/org/add', methods=['POST'])
def add_organization():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    if len(phone) > 20: 
        return "Your phone number should be under 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    active = False
    if 'active' in data:
        active = data.get('active') == 'true'
    type= data.get('type')

    new_org_record = Organization(name, phone, city, state, type, active='t')
    db.session.add(new_org_record)
    db.session.commit()
    
    return("Organization added"), 201


#READ **************************************
# Get all active users
@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    user_records = db.session.query(Users).filter(Users.active==True).all()

    if user_records:
        users = []
        for u in user_records:
            user_record = get_user_from_object(u)
            users.append(user_record)
        return jsonify(users), 200

    return 'No users found', 404

@app.route('/user/get/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not is_valid_uuid(user_id):
        return jsonify(f"User {user_id} not found"), 404

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify("User not found"), 404

 
    return jsonify(get_user_from_object(user_record)), 200

@app.route('/org/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
    if not is_valid_uuid(org_id):
        return jsonify(f"Organizaton {org_id} not found"), 404

    org_record= db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if not org_record:
        return jsonify("Organization not found"), 404

    
    return jsonify(), 200


#UPDATE **************************************
@app.route('/user/update/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def update_user_by_id(user_id):

    request_params = request.json


    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if 'first_name' in request_params:
        user_record.first_name = request_params['first_name']
    if 'last_name' in request_params:
        user_record.last_name = request_params['last_name']
    if 'email' in request_params:
        user_record.email = request_params['email']
    if 'phone' in request_params:
        user_record.phone = request_params['phone']
    if 'city' in request_params:
        user_record.city = request_params['city']
    if 'state' in request_params:
        user_record.state = request_params['state']
    if 'org_id' in request_params:
        user_record.org_id = request_params['org_id']
    if 'active' in request_params:
        user_record.active = request_params['active']
    
    db.session.commit()

    return get_user_by_id(user_id), 200

@app.route('/organization/update/<org_id>', methods=['POST','PATCH','PUT'])
def update_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404

    request_params = request.json

    org_record = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if 'name' in request_params:
        org_record.name = request_params['name']
    if 'phone' in request_params:
        org_record.phone = request_params['phone']
    if 'city' in request_params:
        org_record.city = request_params['city']
    if 'state' in request_params:
        org_record.state = request_params['state']
    if 'type' in request_params:
        org_record.type = request_params['type']
    if 'active' in request_params:
        org_record.active = request_params['active']

    db.session.commit()

    return get_user_by_id(org_id), 200
    

#DELETE **************************************
@app.route('/user/delete', methods=['POST'])
def delete_user():
    data = request.json


    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email') #None
    if not email:
        return "Email must not be an empty str", 400
    phone = data.get('phone')
    if len(phone) > 20: 
        return "Your phone number should be under 20 characters", 400
    city = data.get('city')
    state= data.get('state')
    # org_id = data.get('org_id')

    new_user_record = Users(first_name, last_name, email, phone, city, state)
    db.session.delete(new_user_record) # deleted from db.Model 
    db.session.commit()

    return "User deleted", 201



@app.route('/org/delete', methods=['POST'])
def delete_organization():
    data = request.json

    name = data.get('name')
    phone = data.get('phone')
    if len(phone) > 20: 
        return "Your phone number should be under 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    active = False
    if 'active' in data:
        active = data.get('active') == 'true'
    type= data.get('type')

    org_record = Organization(name, phone, city, state, type, active='t')
    db.session.delete(org_record)
    db.session.commit()

    return("Organization deleted"), 201

#DEACTIVATE **************************************

@app.route('/user/deactivate/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_user_by_id(user_id):
    try:
        user = db.session.query(Users).filter(Users.user_id == user_id).first()
        user.active = False 
        db.session.commit()
        return get_user_by_id(user_id), 200
    except user_exists:
        return jsonify(f"User {user_id} not found"), 404
        

@app.route('/org/deactivate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_org_by_id(org_id):
    try:
        org = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        org.active = False 
        db.session.commit()
        return get_org_by_id(org_id), 200
    except org_exists:
        return jsonify(f"Organization {org_id} not found"), 404

# #ACTIVATE **************************************

@app.route('/user/activate/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_user_by_id(user_id):
    try:
        user = db.session.query(Users).filter(Users.user_id == user_id).first()
        user.active = False 
        db.session.commit()
        return get_user_by_id(user_id), 200
    except user_exists:
        return jsonify(f"User {user_id} not found"), 404


@app.route('/org/activate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_org_by_id(org_id):
    try:
        org = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        org.active = False 
        db.session.commit()
        return get_org_by_id(org_id), 200
    except org_exists:
        return jsonify(f"Organization {org_id} not found"), 404




if __name__ == '__main__': 
    create_all()
    app.run(host='0.0.0.0', port=8086)