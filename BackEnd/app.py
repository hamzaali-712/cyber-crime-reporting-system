from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from models import Officer, Admin, Complaint  # Assuming MongoEngine is used here
from utils import encrypt_password, validate_login, validate_complaint  # Assuming you've defined these utils

app = Flask(__name__)

# MongoDB Atlas Connection String
app.config['MONGO_URI'] = 'mongodb+srv://hamzatalwarali012_db_user:EpDCYYYpnWqvs0Y1@cluster0.1lfkike8.mongodb.net/CyberCrimeDB?retryWrites=true&w=majority'

# MongoDB Initialization
mongo = PyMongo(app)

# Secret Key for Sessions
app.secret_key = 'your_secret_key'

# Routes

# Index Route
@app.route('/')
def index():
    return render_template('index.html')

# Login Route for Officers and Admins
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']
    user_type = request.form['user_type']  # 'officer' or 'admin'

    # Validate login
    if validate_login(user_id, password, user_type):
        session['user_id'] = user_id
        session['user_type'] = user_type
        return redirect(url_for(f'{user_type}_dashboard'))
    return 'Invalid credentials', 401

# Officer Dashboard
@app.route('/officer_dashboard')
def officer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'officer':
        return redirect(url_for('index'))
    
    # Fetch officer from MongoDB using MongoEngine
    officer = mongo.db.officers.find_one({'officer_id': session['user_id']})
    
    # Fetch complaints assigned to the officer
    complaints = list(mongo.db.complaints.find({'officer_assigned': officer['officer_id']}))

    return render_template('officer_dashboard.html', officer=officer, complaints=complaints)

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))

    # Fetch admin from MongoDB
    admin = mongo.db.admins.find_one({'admin_id': session['user_id']})

    # Fetch all officers from MongoDB
    officers = list(mongo.db.officers.find())

    return render_template('admin_dashboard.html', admin=admin, officers=officers)

# Register Officer (Only Admin Access)
@app.route('/register_officer', methods=['POST'])
def register_officer():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('index'))

    officer_data = request.form
    officer = {
        'officer_id': officer_data['officer_id'],
        'name': officer_data['name'],
        'access_key': encrypt_password(officer_data['access_key']),  # Encrypt the password
    }

    # Insert into MongoDB
    mongo.db.officers.insert_one(officer)

    return redirect(url_for('admin_dashboard'))

# Create Complaint
@app.route('/create_complaint', methods=['POST'])
def create_complaint():
    complaint_data = request.form
    if validate_complaint(complaint_data):
        complaint = {
            'complaint_id': complaint_data['complaint_id'],
            'victim_name': complaint_data['victim_name'],
            'crime_type': complaint_data['crime_type'],
            'details': complaint_data['details'],
            'status': 'pending',  # Default status
        }
        
        # Insert into MongoDB
        mongo.db.complaints.insert_one(complaint)
        
        return jsonify({"message": "Complaint submitted successfully!"}), 201
    return jsonify({"message": "Invalid complaint data!"}), 400

# Run Application
if __name__ == '__main__':
    app.run(debug=True)
