import uuid
from datetime import datetime

from src.common.database import Database


class GarmentICO(object):

    def __init__(self, district, garment_type, wage_per_unit, cutting_charges, user_id,
                 garment_name=None, last_updated=None, _id=None):
        self.last_updated = datetime.combine(datetime.now().date(), datetime.now().time())
        self.district = district
        self.garment_type = garment_type
        self.garment_name = garment_name
        self.wage_per_unit = wage_per_unit
        self.cutting_charges = cutting_charges
        self.user_id = user_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='GarmentICO', data=self.json())

    @classmethod
    def update_ico_garment(cls, garment_id, district, garment_type, wage_per_unit,
                           cutting_charges, user_id):
        Database.update_garment_ico(collection='GarmentICO', query={'_id': garment_id}, district=district,
                                    last_updated=datetime.combine(datetime.now().date(), datetime.now().time()),
                                    garment_type=garment_type, wage_per_unit=wage_per_unit,
                                    cutting_charges=cutting_charges, user_id=user_id)

    def json(self):
        return {
            'last_updated': self.last_updated,
            'district': self.district,
            'wage_per_unit': self.wage_per_unit,
            'garment_type': self.garment_type,
            'garment_name': self.garment_name,
            'cutting_charges': self.cutting_charges,
            'user_id': self.user_id,
            '_id': self._id,
        }

    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='GarmentICO', query={'_id': _id})
