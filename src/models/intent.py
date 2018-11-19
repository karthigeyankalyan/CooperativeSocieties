import uuid
from datetime import datetime

from src.common.database import Database


class Intent(object):

    def __init__(self, intent_id, district, center, received_date, garment_type, units_required, units_received,
                 deadline, total_wages, units_pm, user_id, set_id, eo, garment_size, units_assigned=None,
                 _id=None, cut_piece_units=None, stitched_units=None, units_sanctioned=None):
        self.intent_id = intent_id
        self.district = district
        self.center = center
        self.set_id = set_id
        self.eo = eo
        if received_date:
            self.received_date = (datetime.combine(datetime.strptime(received_date, '%Y-%m-%d').date(),
                                                   datetime.now().time()))
        else:
            self.received_date = received_date
        self.garment_type = garment_type
        self.garment_size = garment_size
        self.units_required = int(units_required)
        self.units_assigned = 0 if units_assigned is None else int(units_assigned)
        self.units_received = int(units_received)
        if deadline:
            self.deadline = (datetime.combine(datetime.strptime(deadline, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            self.deadline = deadline
        self.total_wages = total_wages
        self.cut_piece_units = cut_piece_units
        self.stitched_units = stitched_units
        self.units_pm = units_pm
        self.user_id = user_id
        self.units_sanctioned = 0 if units_sanctioned is None else int(units_sanctioned)
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='intents', data=self.json())

    @classmethod
    def update_intent_district(cls, _id, district, center, received_date, garment_type, units_required, units_received,
                               deadline, total_wages, units_pm, set_id, eo):
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

        Database.update_intent(collection='intents', query={'_id': _id}, district=district,
                               center=center, garment_type=garment_type, received_date=received_date,
                               units_required=units_required, units_received=units_received, deadline=deadline,
                               total_wages=total_wages, units_pm=units_pm, set_id=set_id, eo=eo)

    @classmethod
    def update_assigned(cls, _id, units_assigned, units_received):
        Database.update_assigned_units(collection='intents', query={'_id': _id}, units_assigned=units_assigned,
                                       units_received=units_received)

    @classmethod
    def update_transaction_delete(cls, _id, units_assigned_new):
        Database.update_transaction_delete(collection='intents', query={'_id': _id},
                                           units_assigned_new=units_assigned_new)

    def json(self):
        return {
            'intent_id': self.intent_id,
            'district': self.district,
            'center': self.center,
            'received_date': self.received_date,
            'garment_type': self.garment_type,
            'garment_size': self.garment_size,
            'units_required': self.units_required,
            'units_assigned': self.units_assigned,
            'units_received': self.units_received,
            'deadline': self.deadline,
            'total_wages': self.total_wages,
            'units_pm': self.units_pm,
            'user_id': self.user_id,
            'set_id': self.set_id,
            'eo': self.eo,
            '_id': self._id,
        }

    @classmethod
    def from_mongo(cls, _id):
        Intent = Database.find_one(collection='intents', query={'_id': _id})
        return cls(**Intent)

    @classmethod
    def find_by_district(cls, district):
        intent = Database.find(collection='intents', query={'district': district})
        return [cls(**inten) for inten in intent]

    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='intents', query={'_id': _id})

