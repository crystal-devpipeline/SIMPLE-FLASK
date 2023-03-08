from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from users import Users, user_schema, users_schema
from organizations import Organizations, org_schema, orgs_schema, public_org_schema, public_orgs_schema
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
    org = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    if org:
        return True
    return False



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
    age = data.get('age')
    org_id = data.get('org_id')

    new_user_record = Users(first_name, last_name, email, phone, city, state, age, org_id)
    db.session.add(new_user_record) 
    db.session.commit()

    return jsonify(user_schema.dump(new_user_record)), 201


@app.route('/org/add', methods=['POST'])
def add_organization():
    data = request.json
    name = data.get('name')
    if not name or len(name) < 1:
        return "Organization name must not be an empty str", 400
    phone = data.get('phone')
    if len(phone) > 20: 
        return "Your phone number should be under 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    active = True
    if 'active' in data:
        active = data.get('active')
    type= data.get('type')

    new_org = Organizations(name, phone, city, state, type, active)
    db.session.add(new_org)
    db.session.commit()
    
    return jsonify(org_schema.dump(new_org)), 201


#READ **************************************
# Get all active users
@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    user_records = db.session.query(Users).filter(Users.active==True).all()

    if user_records:
        return jsonify(users_schema.dump(user_records)), 200

    return 'No users found', 404


@app.route('/user/get/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not is_valid_uuid(user_id):
        return jsonify(f"User {user_id} not found"), 404

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify("User not found"), 404

    return jsonify(user_schema.dump(user_record)), 200


@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
    orgs_record = db.session.query(Organizations).filter(Organizations.active==True).all()

    if orgs_record:
        return jsonify(orgs_schema.dump(orgs_record)), 200
       
    return jsonify("No organizations found"), 404

    
@app.route('/org/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()  
    
    if not org_record:
        return jsonify("Organization not found"), 404
    if org_record:
        return jsonify(org_schema.dump(org_record)), 200
    
@app.route('/org/public/get', methods=['GET'])
def get_public_org_info():
    orgs_record = db.session.query(Organizations).filter(Organizations.active==True).all()

    if orgs_record:
        return jsonify(public_orgs_schema.dump(orgs_record)), 200
       
    return jsonify("Hey Yo! No organizations found"), 404
    
    return(), 200
  
   
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
    if 'age' in request_params:
        user_record.age = request_params['age']
    if 'org_id' in request_params:
        user_record.org_id = request_params['org_id']
    if 'active' in request_params:
        user_record.active = request_params['active']
    
    db.session.commit()
    return jsonify(user_schema.dump(user_record)), 201


@app.route('/org/update/<org_id>', methods=['POST','PATCH','PUT'])
def update_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"Organization {org_id} not found"), 404

    request_params = request.json
    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

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
        org_record.active = request_params.get['active'] != 'false'

    db.session.commit()
    return jsonify(org_schema.dump(org_record)), 201
    

#DELETE **************************************
@app.route('/user/delete/<user_id>', methods=['DELETE'])
def user_delete(user_id):
    user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
    if user_data:
        db.session.delete(user_data)
        db.session.commit()
    
    return "User deleted", 201


@app.route('/org/delete/<org_id>', methods=['DELETE'])
def org_delete(org_id):
    org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    if org_data:
        db.session.delete(org_data)
        db.session.commit()
    
    return "Organization deleted", 201


#DEACTIVATE **************************************
@app.route('/user/deactivate/<user_id>', methods=['POST', 'PUT', 'PATCH'])#TODO: make this work
def deactivate_user_by_id(user_id):
    return activate_user_by_id(user_id, False)


@app.route('/org/deactivate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_org_by_id(org_id):
    try:
        org = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
        org.active = False 
        db.session.commit()
        return get_org_by_id(org_id)
    except org_exists:
        return jsonify(f"Organization {org_id} not found"), 404

# #ACTIVATE **************************************

@app.route('/user/activate/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_user_by_id(user_id, set_active=True):
    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify(f"User {user_id} not found"), 404
    
    user_record.active = set_active
    db.session.commit()


    return jsonify(user_schema.dump(user_record)), 200

  

@app.route('/org/activate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_org_by_id(org_id):
    try:
        org = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
        org.active = True 
        db.session.commit()
    except org_exists:
        return jsonify(f"Organization {org_id} not found"), 404

    return get_org_by_id(org_id)



if __name__ == '__main__': 
    create_all()
    app.run(host='0.0.0.0', port=8086)