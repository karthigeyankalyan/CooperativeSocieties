import os

import pymongo
from bson import ObjectId
from bson.errors import InvalidId


class Database(object):
    # URI = "mongodb://127.0.0.1:27017"
    # DATABASE = None
    #
    # @staticmethod
    # def initialize():
    #     client = pymongo.MongoClient(Database.URI)
    #     Database.DATABASE = client['Coop']

    URI = os.environ['MONGODB_URI']
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['heroku_1n536d42']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def is_valid(oid):
        try:
            ObjectId(oid)
            return True
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update_intent(collection, query, district, center, garment_type, received_date, units_required,
                      units_received, deadline, total_wages, units_pm, set_id, eo):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'center': center,
                                                                         'received_date': received_date,
                                                                         'block': garment_type,
                                                                         'units_required': units_required,
                                                                         'units_received': units_received,
                                                                         'deadline': deadline,
                                                                         'total_wages': total_wages,
                                                                         'set_id': set_id,
                                                                         'eo': eo,
                                                                         'units_pm': units_pm}}, True)

    @staticmethod
    def update_installment(collection, query, district, center, garment_type, received_date, units_required,
                           deadline, total_wages, units_pm, set_id, eo, installment_num):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'center': center,
                                                                         'uploaded_date': received_date,
                                                                         'block': garment_type,
                                                                         'units_required': units_required,
                                                                         'deadline': deadline,
                                                                         'set_id': set_id,
                                                                         'eo': eo,
                                                                         'total_wages': total_wages,
                                                                         'installment_num': installment_num,
                                                                         'units_pm': units_pm}}, True)

    @staticmethod
    def update_received_units(collection, query, cut_piece_units, material_received_date):
        return Database.DATABASE[collection].update_one(query, {'$set': {'cut_piece_units': cut_piece_units,
                                                                         'material_received_date':
                                                                             material_received_date}}, True)

    @staticmethod
    def update_assigned_units(collection, query, units_assigned, units_received):
        return Database.DATABASE[collection].update_one(query, {'$set': {'units_assigned': units_assigned,
                                                                         'units_received': units_received}}, True)

    @staticmethod
    def update_garment_ico(collection, query, last_updated, district, garment_type, wage_per_unit,
                           cutting_charges, user_id):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'last_updated': last_updated,
                                                                         'garment_type': garment_type,
                                                                         'wage_per_unit': wage_per_unit,
                                                                         'cutting_charges': cutting_charges,
                                                                         'user_id': user_id}}, True)

    @staticmethod
    def update_member_details(name, district, center, enrollment_date, member_id, address, contact_details,
                              query, collection, user_id, bank_account_number, bank_ifsc_code, bank_name,
                              aadhar, status, dob):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'center': center,
                                                                         'name': name,
                                                                         'user_id': user_id,
                                                                         'enrollment_date': enrollment_date,
                                                                         'bank_account_number': bank_account_number,
                                                                         'bank_ifsc_code': bank_ifsc_code,
                                                                         'bank_name': bank_name,
                                                                         'wage_per_unit': member_id,
                                                                         'address': address,
                                                                         'aadhar_no': aadhar,
                                                                         'date_of_birth': dob,
                                                                         'social_status': status,
                                                                         'contact_details': contact_details}}, True)

    @staticmethod
    def update_member_shares(share, query, collection, thrift):
        return Database.DATABASE[collection].update_one(query, {'$set': {'thrift': thrift,
                                                                         'share': share}}, True)

    @staticmethod
    def update_wages_paid(query, collection, wage_paid):
        return Database.DATABASE[collection].update_one(query, {'$set': {'wage_paid': wage_paid}}, True)

    @staticmethod
    def update_status(query, collection):
        return Database.DATABASE[collection].update_one(query, {'$set': {'status': "Completed"}}, True)

    @staticmethod
    def update_status_reverse(query, collection):
        return Database.DATABASE[collection].update_one(query, {'$set': {'status': "Ongoing"}}, True)

    @staticmethod
    def update_overall_wages_paid(query, collection, wage_paid, wage_entitled):
        return Database.DATABASE[collection].update_one(query, {'$set': {'overall_wage_paid': wage_paid,
                                                                         'overall_wage_entitled': wage_entitled}}, True)

    @staticmethod
    def update_member_transaction(name, member_id, garment_name, wage_expected, advance_paid, remaining_amount,
                                  no_of_units, deadline, units_returned, query, collection, user_id,
                                  transaction_status, thrift, share, issue_date, deductions):
        return Database.DATABASE[collection].update_one(query, {'$set': {'garment_name': garment_name,
                                                                         'wage_expected': wage_expected,
                                                                         'advance_paid': advance_paid,
                                                                         'deductions': deductions,
                                                                         'remaining_amount': remaining_amount,
                                                                         'name': name,
                                                                         'thrift': thrift,
                                                                         'share': share,
                                                                         'member_id': member_id,
                                                                         'user_id': user_id,
                                                                         'transaction_status': transaction_status,
                                                                         'no_of_units': no_of_units,
                                                                         'deadline': deadline,
                                                                         'issue_date': issue_date,
                                                                         'units_returned': units_returned}}, True)

    @staticmethod
    def update_eo_details(collection, query, name, district, block, society_name, travel_charge,
                          user_id):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'block': block,
                                                                         'name': name,
                                                                         'society_name': society_name,
                                                                         'travel_charge': travel_charge,
                                                                         'user_id': user_id}}, True)

    @staticmethod
    def update_garment_ovr(collection, query, last_updated, district, garment_type, wage_per_unit,
                           cutting_charges, deductions, user_id, garment_name, society):
        return Database.DATABASE[collection].update_one(query, {'$set': {'district': district,
                                                                         'last_updated': last_updated,
                                                                         'society': society,
                                                                         'garment_type': garment_type,
                                                                         'garment_name': garment_name,
                                                                         'wage_per_unit': wage_per_unit,
                                                                         'cutting_charges': cutting_charges,
                                                                         'deductions': deductions,
                                                                         'user_id': user_id}}, True)

    @staticmethod
    def delete_from_mongo(collection, query):
        Database.DATABASE[collection].remove(query)

    @staticmethod
    def change_password(collection, query, password):
        return Database.DATABASE[collection].update_one(query, {'$set': {'password': password}}, True)
