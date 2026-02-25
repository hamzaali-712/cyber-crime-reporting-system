from cryptography.fernet import Fernet
import hashlib

# Generate and save a key for encryption (Do this only once and store securely)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load encryption key
def load_key():
    return open("secret.key", "rb").read()

# Encrypt password using Fernet
def encrypt_password(password):
    key = load_key()
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    return encrypted_password

# Validate login credentials
def validate_login(user_id, password, user_type):
    if user_type == 'officer':
        user = Officer.get_officer(user_id)
    else:
        user = Admin.get_admin(user_id)

    if user and user['access_key'] == encrypt_password(password):
        return True
    return False

# Validate complaint data
def validate_complaint(complaint_data):
    required_fields = ['complaint_id', 'victim_name', 'crime_type']
    for field in required_fields:
        if field not in complaint_data or not complaint_data[field]:
            return False
    return True
