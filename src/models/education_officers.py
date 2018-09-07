import uuid

from src.common.database import Database


class EducationOfficers(object):

    def __init__(self, name, district, block, society_name, travel_charge, cutting_charges=None, user_id=None, _id=None):
        self.name = name
        self.district = district
        self.block = block
        self.cutting_charges = cutting_charges
        self.society_name = society_name
        self.travel_charge = travel_charge
        self.user_id = user_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='eoDetails', data=self.json())

    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='eoDetails', query={'_id': _id})

    @classmethod
    def update_eo_details(cls, name, district, block, society_name, travel_charge, user_id, eo_id):
        Database.update_eo_details(collection='eoDetails', query={'_id': eo_id}, name=name, district=district,
                                   block=block, society_name=society_name, travel_charge=travel_charge, user_id=user_id)

    def json(self):
        return {
            'district': self.district,
            'block': self.block,
            'name': self.name,
            'society_name': self.society_name,
            'cutting_charges': self.cutting_charges,
            'travel_charge': self.travel_charge,
            'user_id': self.user_id,
            '_id': self._id,
        }
