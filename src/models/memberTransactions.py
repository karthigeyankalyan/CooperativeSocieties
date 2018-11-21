import uuid
from datetime import datetime

from src.common.database import Database


class memberTransactions(object):

    def __init__(self, name, member_id, garment_type, district, society, wage_expected, advance_paid, intent_id,
                 installment_id, issue_date, no_of_units, deadline, bank_account, ifsc, remaining_amount=None,
                 units_returned=None, thrift=None, _id=None, transaction_status=None, share=None, garment_name=None,
                 deductions=None, garment_size=None, contact_details=None):
        self.name = name
        self.member_id = member_id
        self.bank_account = bank_account
        self.ifsc = ifsc
        self.district = district
        self.society = society
        self.garment_type = garment_type
        self.garment_name = garment_name
        self.garment_size = garment_size
        self.wage_expected = float(wage_expected)
        self.advance_paid = float(advance_paid)
        self.deductions = float(deductions)
        self.transaction_status = transaction_status
        self.remaining_amount = (float(wage_expected)-float(advance_paid)) if remaining_amount is None else remaining_amount
        self.thrift = float(thrift) if thrift is not None else thrift
        self.share = float(share) if thrift is not None else share
        self.intent_id = intent_id
        self.installment_id = installment_id
        self.contact_details = contact_details
        self.no_of_units = int(no_of_units)
        self.units_returned = 0 if units_returned is None else units_returned

        if deadline:
            self.deadline = (datetime.combine(datetime.strptime(deadline, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            self.deadline = deadline

        if issue_date:
            self.issue_date = (datetime.combine(datetime.strptime(issue_date, '%Y-%m-%d').date(),
                                                datetime.now().time()))
        else:
            self.issue_date = issue_date

        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='memberTransactions', data=self.json())

    @classmethod
    def update_member_transaction(cls, name, member_id, garment_name, wage_expected, advance_paid, remaining_amount,
                                  no_of_units, deadline, transaction_id, units_returned, user_id, transaction_status,
                                  thrift, share, issue_date, deductions, garment_size):
        if deadline:
            deadline = (datetime.combine(datetime.strptime(deadline, '%Y-%m-%d').date(),
                                         datetime.now().time()))
        else:
            deadline = deadline

        if issue_date:
            issue_date = (datetime.combine(datetime.strptime(issue_date, '%Y-%m-%d').date(),
                                           datetime.now().time()))
        else:
            issue_date = issue_date

        Database.update_member_transaction(collection='memberTransactions', query={'_id': transaction_id},
                                           garment_name=garment_name, wage_expected=int(wage_expected),
                                           advance_paid=int(advance_paid), remaining_amount=int(remaining_amount),
                                           no_of_units=int(no_of_units), name=name, member_id=member_id,
                                           units_returned=units_returned, deadline=deadline, user_id=user_id,
                                           transaction_status=transaction_status, thrift=int(thrift), share=int(share),
                                           issue_date=issue_date, deductions=deductions, garment_size=garment_size)

    @classmethod
    def update_paid_wages(cls, _id, wage_paid):
        Database.update_wages_paid(collection='memberTransactions', query={'_id': _id}, wage_paid=wage_paid)

    def json(self):
        return {
            'name': self.name,
            'member_id': self.member_id,
            'bank_account': self.bank_account,
            'ifsc': self.ifsc,
            'district': self.district,
            'society': self.society,
            'garment_type': self.garment_type,
            'garment_name': self.garment_name,
            'garment_size': self.garment_size,
            'wage_expected': self.wage_expected,
            'advance_paid': self.advance_paid,
            'deductions': self.deductions,
            'remaining_amount': self.remaining_amount,
            'thrift': self.thrift,
            'intent_id': self.intent_id,
            'transaction_status': self.transaction_status,
            'installment_id': self.installment_id,
            'no_of_units': self.no_of_units,
            'deadline': self.deadline,
            'issue_date': self.issue_date,
            'units_returned': self.units_returned,
            'contact_details': self.contact_details,
            '_id': self._id
        }

    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='memberTransactions', query={'_id': _id})
