# Before SQLAlchemy
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt2' user='crystalsorensen' host='localhost'")

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR,
        email VARCHAR NOT NULL UNIQUE,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR,
        active BOOLEAN NOT NULL DEFAULT True,
        org_id INT
    );
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        org_ig SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR,
        active VARCHAR NOT NULL DEFAULT True,
        type VARCHAR
    )

''')
conn.commit()

# user_fields is a tuple of the following fields:(user_id, first_name, last_name, email, phone, city, state, org_id, active)
def get_user_from_list(user_fields):
    return{
           'user_id':user_fields[0],
            'first_name':user_fields[1],
            'last_name':user_fields[2],
            'email':user_fields[3],
            'phone':user_fields[4],
            'city':user_fields[5],
            'state':user_fields[6],
            'organization':{
                'org_id':user_fields[9],
                'name':user_fields[10],
                'phone':user_fields[11],
                'city':user_fields[12],
                'state':user_fields[13],
                'active':user_fields[14],
                'type':user_fields[15],
            },
            'active':user_fields[8]
        }   

def get_org_from_list(org_fields):
    return{
        'org_id':org_fields[0],
        'name':org_fields[1],
        'phone':org_fields[2],
        'city':org_fields[3],
        'state':org_fields[4],
        'active':org_fields[5],
        'type':org_fields[5]
    }   
    

def user_exists(user_id):
    if not user_id.isnumeric():
        return False

def org_exists(org_id):
    if not org_id.isnumeric():
        return False


# CREATE ************************************
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
    org_id = data.get('org_id')

    try:
        cursor.execute('''
                INSERT INTO users (first_name, last_name, email, phone, city, state, org_id)
                VALUES (%s, %s, %s,%s, %s, %s, %s)
                ''', (first_name, last_name, email, phone, city, state, org_id))
    except psycopg2.errors.UniqueViolation:
        cursor.execute("ROLLBACK")
        return jsonify("Error adding user! YOu have a duplicate field."), 400
    
    conn.commit()
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

    cursor.execute(
        '''
        INSERT INTO users (name, phone, city, state, active, type)
        VALUES (%s, %s, %s,%s, %s,%s)
        ''', (name, phone, city, state, active, type))
    conn.commit()
    
    return("Organization added"), 201



# READ ***********************************
@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    cursor.execute('''
        SELECT 
            u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active, o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type 
        FROM users u 
            LEFT OUTER JOIN organizations o
                ON u.org_id = o.org_id
        WHERE u.active='t';
    ''')

    results = cursor.fetchall()

    if results:
        users = []
        for u in results:
            user_record = get_user_by_id(u)

            users.append(user_record)
        return jsonify(users), 200

    return 'No users found', 404

@app.route('/user/get/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found"), 404
    cursor.execute('''
    SELECT 
        u.user_id=%s, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active, o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type 
    FROM users u 
        LEFT OUTTER JOIN organizations o
            ON u.org_id = o.org_id
    WHERE user_id=%s;
    ''', (user_id,))    
    u = cursor.fetchone()

    if not u:
        return jsonify(f"User {user_id} not found!"), 404
        
    user_record = get_user_from_list(u)

    return jsonify(user_record), 200

@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
    orgs_records = db.session.query(Organizations).filter(Organization.active==True).all()
    
    return(), 200

@app.route('/org/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404
    
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s, first_name, last_name, email, phone, city, state, org_id, active FROM users WHERE org_id=%s;", (org_id,))
    u = cursor.fetchone()

    if not u:
        return (f"Organization {org_id} not found!"), 404
    org_record = get_user_from_list(u)
        
    return jsonify(org_record), 200


#  UPDATE ****************************
@app.route('/user/update/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def update_user_by_id(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found!"), 400

    request_params = request.json

    fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'active']

    update_fields = []
    field_values = []

    for field in fields:
        if field in request_params.keys():
            update_fields.append(f'{field}=%s')
            field_values.append(request_params[field])
        else:
            return jsonify(f"Field {field} is invalid"), 400
    field_values.append(user_id)
        
    update_query = "UPDATE users SET " + ','.join(update_fields) + " WHERE user_id=%s"

    cursor.execute(update_query, field_values)
    conn.commit()

    return get_user_by_id(user_id), 200

    

@app.route('/org/update/<org_id>', methods=['POST','PATCH','PUT'])
def update_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404

    request_params = request.json

    fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'active']

    update_fields = []
    field_values = []

    for field in fields:
        if field in request_params.keys():
            update_fields.append(f'{field}=%s')
            field_values.append(request_params[field])
        else:
            return jsonify(f"Field {field} is invalid"), 400

    field_values.append(org_id)
    update_query = "UPDATE users SET " + ','.join(update_fields) + " WHERE user_id=%s"

    cursor.execute(update_query, field_values)
    conn.commit()
        
    return get_user_by_id(org_id), 200


# DELETE ************************************
@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found"), 404
    
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"User #{user_id} not found"), 404
    
    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    
    return(f"User #{user_id} Deleted! "), 200

@app.route('/organization/delete/<org_id>', methods=['DELETE'])
def delete_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404
    
    cursor.execute("SELECT * FROM users WHERE org_id=%s", (org_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"User #{org_id} not found"), 404
    
    cursor.execute("DELETE FROM organizations WHERE org_id=%s", (org_id,))
    
    return(f"Organization # {org_id} Deleted! "), 200

# DEACTIVATE ************************************
@app.route('/user/deactivate/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_user_by_id(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found"), 404
    
    cursor.execute("SELECT * FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"User {user_id} not found"), 404

    cursor.execute("UPDATE users SET active='false' WHERE user_id=%s", (user_id,))
    conn.commit()
    
    return ("user deactivated"), 200


@app.route('/organization/deactivate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404
    
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"Organization # {org_id} not found"), 404

    cursor.execute("UPDATE organizations SET active='false' WHERE org_id=%s", (org_id,))
    conn.commit()
    
    return ("Organization deactivated"), 200


#  ACTIVATE ************************************
@app.route('/user/activate/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def activate_user_by_id(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found"), 404

    cursor.execute("SELECT * FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchall()

    if not results:
        return (f"User {user_id} not found"), 404

    cursor.execute("UPDATE users SET active='t' WHERE user_id%s;", (user_id))
    conn.commit()

    return(f"User {user_id} activated"), 200

@app.route('/organization/activate/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_org_by_id(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found"), 404
    
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s;", (org_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"Organization#: {org_id} not found"), 404

    cursor.execute("UPDATE organizations SET active='true' WHERE org_id=%s", (org_id,))
    conn.commit()
    
    return('Organization Activated'), 200

    



if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8086)

# I think you may just need to put a db.init() in this file if you're running app.py, kinda similar to youre app_sqlalchemy.py. That plus db.create_all(). -Blake