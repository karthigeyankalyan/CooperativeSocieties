import uuid
from datetime import datetime

from src.common.database import Database


class GarmentDistrict(object):

    def __init__(self, district, garment_type, garment_name, wage_per_unit, cutting_charges, user_id,
                 deductions, society, last_updated=None, _id=None):
        self.last_updated = datetime.combine(datetime.now().date(), datetime.now().time())
        self.district = district
        self.society = society
        self.garment_type = garment_type
        self.garment_name = garment_name
        self.wage_per_unit = wage_per_unit
        self.cutting_charges = cutting_charges
        self.deductions = deductions
        self.user_id = user_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='GarmentDistrict', data=self.json())

    @classmethod
    def update_garment_district(cls, garment_id, district, garment_type, wage_per_unit, society,
                                cutting_charges, deductions, user_id, garment_name):
        Database.update_garment_ovr(collection='GarmentDistrict', query={'_id': garment_id}, district=district,
                                    last_updated=datetime.combine(datetime.now().date(), datetime.now().time()),
                                    garment_type=garment_type, wage_per_unit=wage_per_unit,
                                    cutting_charges=cutting_charges, deductions=deductions, user_id=user_id,
                                    garment_name=garment_name, society=society)

    def json(self):
        return {
            'last_updated': self.last_updated,
            'district': self.district,
            'society': self.society,
            'garment_name': self.garment_name,
            'garment_type': self.garment_type,
            'wage_per_unit': self.wage_per_unit,
            'block': self.garment_type,
            'cutting_charges': self.cutting_charges,
            'deductions': self.deductions,
            'user_id': self.user_id,
            '_id': self._id,
        }

    @classmethod
    def delete_from_mongo(cls, _id):
        Database.delete_from_mongo(collection='GarmentDistrict', query={'_id': _id})


