from cryptography.fernet import Fernet
from flask_pymongo import PyMongo

# MongoDB Document Definitions (not MongoEngine)
# Assuming `mongo` is passed here

class Officer:
    def __init__(self, officer_id, name, access_key):
        self.officer_id = officer_id
        self.name = name
        self.access_key = access_key

    @staticmethod
    def get_officer(officer_id):
        return mongo.db.officers.find_one({'officer_id': officer_id})

    @staticmethod
    def get_all_officers():
        return list(mongo.db.officers.find())

class Admin:
    def __init__(self, admin_id, name, access_key):
        self.admin_id = admin_id
        self.name = name
        self.access_key = access_key

    @staticmethod
    def get_admin(admin_id):
        return mongo.db.admins.find_one({'admin_id': admin_id})

class Complaint:
    def __init__(self, complaint_id, victim_name, crime_type, details, officer_assigned=None, status='pending'):
        self.complaint_id = complaint_id
        self.victim_name = victim_name
        self.crime_type = crime_type
        self.details = details
        self.officer_assigned = officer_assigned
        self.status = status

    @staticmethod
    def get_complaints(officer_id):
        return list(mongo.db.complaints.find({'officer_assigned': officer_id}))
