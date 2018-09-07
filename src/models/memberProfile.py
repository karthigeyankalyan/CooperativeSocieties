import uuid
from datetime import datetime

from src.common.database import Database


class memberProfile(object):

    def __init__(self, name, district, center, enrollment_date, user_id, member_id, address,
                 outstanding_balance=None, no_of_violations=None, contact_details=None, _id=None,
                 overall_wage_entitled=None, overall_wage_paid=None, bank_account_number=None,
                 bank_ifsc_code=None, bank_name=None):
        self.name = name
        self.district = district
        self.center = center
        self.member_id = member_id
        self.address = address
        self.no_of_violations = no_of_violations
        self.member_overall_thrift = 0
        self.contact_details = contact_details
        self.bank_account_number = bank_account_number
        self.bank_ifsc_code = bank_ifsc_code
        self.bank_name = bank_name
        self.share_value = 0
        self.user_id = user_id

        if enrollment_date:
            self.enrollment_date = (datetime.combine(datetime.strptime(enrollment_date, '%Y-%m-%d').date(),
                                                     datetime.now().time()))
        else:
            self.enrollment_date = enrollment_date

        self.outstanding_balance = outstanding_balance
        self.overall_wage_entitled = overall_wage_entitled
        self.overall_wage_paid = overall_wage_paid
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='members', data=self.json())

    @classmethod
    def update_member(cls, name, district, center, enrollment_date, member_id, address, contact_details,
                      mem_id, user_id, bank_account_number, bank_ifsc_code, bank_name):

        if enrollment_date:
            enrollment_date = (datetime.combine(datetime.strptime(enrollment_date, '%Y-%m-%d').date(),
                                                datetime.now().time()))
        else:
            enrollment_date = enrollment_date

        Database.update_member_details(collection='members', query={'_id': mem_id}, district=district, name=name,
                                       center=center, member_id=member_id, address=address,
                                       contact_details=contact_details, user_id=user_id,
                                       enrollment_date=enrollment_date, bank_account_number=bank_account_number,
                                       bank_ifsc_code=bank_ifsc_code, bank_name=bank_name)

    @classmethod
    def update_member_share(cls, thrift, share, mem_id):
        Database.update_member_shares(collection='members', query={'_id': mem_id}, share=share, thrift=thrift)

    @classmethod
    def update_paid_wages(cls, _id, wage_paid, wage_entitled):
        Database.update_overall_wages_paid(collection='members', query={'_id': _id}, wage_paid=wage_paid,
                                           wage_entitled=wage_entitled)

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
            '_id': self._id,
        }


    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='members', query={'_id': _id})

