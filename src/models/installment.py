import uuid
from datetime import datetime

from src.common.database import Database


class Installment(object):

    def __init__(self, installment_num, intent_id, district, center, units_required, garment_type, uploaded_date,
                 deadline, total_wages, units_pm, user_id, units_received=None, units_assigned=None,  eo=None,
                 garment_size=None, _id=None, set_id=None, material_received_date=None, cut_piece_units=None,
                 status=None, units_sanctioned=None):
        self.intent_id = intent_id
        self.installment_num = installment_num
        self.district = district
        self.center = center
        self.garment_type = garment_type
        self.garment_size = garment_size
        self.set_id = set_id

        if uploaded_date:
            self.uploaded_date = (datetime.combine(datetime.strptime(uploaded_date, '%Y-%m-%d').date(),
                                                   datetime.now().time()))
        else:
            self.uploaded_date = uploaded_date

        if material_received_date:
            self.material_received_date = (datetime.combine(datetime.strptime(material_received_date, '%Y-%m-%d').date(),
                                                            datetime.now().time()))
        else:
            self.material_received_date = material_received_date

        self.units_required = units_required
        self.cut_piece_units = 0 if cut_piece_units is None else cut_piece_units
        self.units_assigned = 0 if units_assigned is None else units_assigned
        self.units_received = 0 if units_received is None else units_received
        self.units_sanctioned = 0 if units_sanctioned is None else units_sanctioned

        if deadline:
            self.deadline = (datetime.combine(datetime.strptime(deadline, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            self.deadline = deadline

        self.total_wages = total_wages
        self.status = "Ongoing"
        self.units_pm = units_pm
        self.eo = eo
        self.user_id = user_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='installments', data=self.json())

    @classmethod
    def update_installments(cls, _id, district, center, received_date, garment_type, units_required,
                            deadline, total_wages, units_pm, set_id, eo, installment_num):
        if deadline:
            deadline = (datetime.combine(datetime.strptime(deadline, '%Y-%m-%d').date(),
                                         datetime.now().time()))
        else:
            deadline = deadline

        if received_date:
            received_date = (datetime.combine(datetime.strptime(received_date, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            received_date = received_date

        Database.update_installment(collection='installments', query={'_id': _id}, district=district,
                                    installment_num=installment_num, center=center, garment_type=garment_type,
                                    received_date=received_date, units_required=units_required,
                                    deadline=deadline, total_wages=total_wages, units_pm=units_pm, set_id=set_id, eo=eo)

    @classmethod
    def update_received(cls, _id, cut_piece_units, material_received_date):

        if material_received_date:
            material_received_date = (datetime.combine(datetime.strptime(material_received_date, '%Y-%m-%d').date(),
                                                       datetime.now().time()))
        else:
            material_received_date = material_received_date

        Database.update_received_units(collection='installments', query={'_id': _id}, cut_piece_units=cut_piece_units,
                                       material_received_date=material_received_date)

    @classmethod
    def update_assigned(cls, _id, units_assigned, units_received):
        Database.update_assigned_units(collection='installments', query={'_id': _id}, units_assigned=units_assigned,
                                       units_received=units_received)

    @classmethod
    def update_status(cls, _id):
        Database.update_status(collection='installments', query={'_id': _id})

    @classmethod
    def update_delivery(cls, _id, units_delivered):
        Database.update_delivery(collection='installments', query={'_id': _id},
                                 units_delivered=units_delivered)

    @classmethod
    def update_status_reverse(cls, _id):
        Database.update_status_reverse(collection='installments', query={'_id': _id})

    def json(self):
        return {
            'intent_id': self.intent_id,
            'installment_num': self.installment_num,
            'district': self.district,
            'center': self.center,
            'garment_type': self.garment_type,
            'garment_size': self.garment_size,
            'set_id': self.set_id,
            'uploaded_date': self.uploaded_date,
            'cut_piece_units': self.cut_piece_units,
            'material_received_date': self.material_received_date,
            'units_required': self.units_required,
            'units_assigned': self.units_assigned,
            'units_received': self.units_received,
            'units_sanctioned': self.units_sanctioned,
            'deadline': self.deadline,
            'total_wages': self.total_wages,
            'status': self.status,
            'units_pm': self.units_pm,
            'user_id': self.user_id,
            'eo': self.eo,
            '_id': self._id,
        }
