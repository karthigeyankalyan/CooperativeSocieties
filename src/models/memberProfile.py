import uuid
from datetime import datetime

from bson import ObjectId

from src.common.database import Database


class memberProfile(object):

    def __init__(self, name, district, center, enrollment_date, user_id, member_id, address, aadhar_no=None,
                 social_status=None, date_of_birth=None, outstanding_balance=None, no_of_violations=None,
                 contact_details=None, _id=None, overall_wage_entitled=None, overall_wage_paid=None,
                 bank_account_number=None, bank_ifsc_code=None, bank_name=None, share_value=None,
                 thrift_value=None, caste=None):
        self.name = name
        self.district = district
        self.center = center
        self.member_id = int(member_id)
        self.address = address
        self.no_of_violations = no_of_violations
        self.member_overall_thrift = thrift_value
        self.contact_details = contact_details
        self.bank_account_number = bank_account_number
        self.bank_ifsc_code = bank_ifsc_code
        self.bank_name = bank_name
        self.share_value = share_value
        self.user_id = user_id
        self.social_status = social_status
        self.caste = caste

        if enrollment_date:
            self.enrollment_date = (datetime.combine(datetime.strptime(enrollment_date, '%Y-%m-%d').date(),
                                                     datetime.now().time()))
        else:
            self.enrollment_date = enrollment_date

        if date_of_birth:
            self.date_of_birth = (datetime.combine(datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
                                                   datetime.now().time()))
        else:
            self.date_of_birth = date_of_birth

        self.outstanding_balance = outstanding_balance
        self.aadhar_no = aadhar_no
        self.overall_wage_entitled = overall_wage_entitled
        self.overall_wage_paid = overall_wage_paid
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='members', data=self.json())

    @classmethod
    def update_member(cls, name, district, center, enrollment_date, member_id, address, contact_details,
                      mem_id, user_id, bank_account_number, bank_ifsc_code, bank_name, aadhar, dob, status,
                      share_value, thrift_value, caste):

        if enrollment_date:
            enrollment_date = (datetime.combine(datetime.strptime(enrollment_date, '%Y-%m-%d').date(),
                                                datetime.now().time()))
        else:
            enrollment_date = enrollment_date

        if dob:
            dob = (datetime.combine(datetime.strptime(dob, '%Y-%m-%d').date(),
                                    datetime.now().time()))
        else:
            dob = enrollment_date

        if Database.is_valid(mem_id):
            Database.update_member_details(collection='members', query={'_id': ObjectId(mem_id)}, district=district,
                                           name=name, center=center, member_id=int(member_id), address=address,
                                           contact_details=contact_details, user_id=user_id, enrollment_date=enrollment_date,
                                           bank_account_number=bank_account_number, bank_ifsc_code=bank_ifsc_code,
                                           bank_name=bank_name, aadhar=aadhar, dob=dob, status=status, share_value=share_value,
                                           thrift_value=thrift_value, caste=caste)
        else:
            Database.update_member_details(collection='members', query={'_id': mem_id}, district=district, name=name,
                                           center=center, member_id=int(member_id), address=address,
                                           contact_details=contact_details, user_id=user_id,
                                           enrollment_date=enrollment_date, bank_account_number=bank_account_number,
                                           bank_ifsc_code=bank_ifsc_code, bank_name=bank_name, aadhar=aadhar,
                                           dob=dob, status=status, share_value=share_value, thrift_value=thrift_value,
                                           caste=caste)

    @classmethod
    def update_member_share(cls, thrift, share, mem_id):
        if Database.is_valid(mem_id):
            Database.update_member_shares(collection='members', query={'_id': ObjectId(mem_id)},
                                          share=share, thrift=thrift)
        else:
            Database.update_member_shares(collection='members', query={'_id': mem_id},
                                          share=share, thrift=thrift)

    @classmethod
    def update_paid_wages(cls, mem_id, wage_paid, wage_entitled):
        if Database.is_valid(mem_id):
            Database.update_overall_wages_paid(collection='members', query={'_id': ObjectId(mem_id)},
                                               wage_paid=wage_paid, wage_entitled=wage_entitled)
        else:
            Database.update_overall_wages_paid(collection='members', query={'_id': mem_id},
                                               wage_paid=wage_paid, wage_entitled=wage_entitled)

    def json(self):
        return {
            'name': self.name,
            'district': self.district,
            'center': self.center,
            'member_id': self.member_id,
            'address': self.address,
            'contact_details': self.contact_details,
            'enrollment_date': self.enrollment_date,
            'bank_account_number': self.bank_account_number,
            'bank_ifsc_code': self.bank_ifsc_code,
            'bank_name': self.bank_name,
            'share_value': self.share_value,
            'outstanding_balance': self.outstanding_balance,
            'current_thrift_value': self.member_overall_thrift,
            'social_status': self.social_status,
            'date_of_birth': self.date_of_birth,
            'aadhar_no': self.aadhar_no,
            'caste': self.caste,
            '_id': self._id,
        }


    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='members', query={'_id': _id})

