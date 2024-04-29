import sqlalchemy

from storage.connection import session as factory

from storage.models import *


def session_decorator(func):
    def wrapper(*args, **kwargs):
        with factory() as session:
            return func(session, *args, **kwargs)
    return wrapper


class DataLayer:

    @staticmethod
    @session_decorator
    def get_all(session, obj):
        return session.query(obj).all()

    @staticmethod
    @session_decorator
    def get_one_by_criteria(session, obj, field, value):
        return session.query(obj).filter(getattr(obj, field) == value).first()

    @staticmethod
    @session_decorator
    def get_one_by_id(session, obj, _id):
        return session.query(obj).get(_id)

    @staticmethod
    @session_decorator
    def create_one(session, obj, data, return_id: bool = False):
        new_obj = obj(
            **data
        )
        try:
            session.add(new_obj)
            if return_id:
                return new_obj.id
        except sqlalchemy.exc.IntegrityError:
            raise
        finally:
            session.commit()

    @staticmethod
    @session_decorator
    def update_one(session, obj, values, _id):
        session.query(obj).filter_by(id=_id).update(**values)
        session.flush()
        session.commit()

    @staticmethod
    @session_decorator
    def delete_one_by_criteria(session, obj, _id):
        session.query(obj).filter_by(id=_id).delete()
        session.commit()


class CityLayer(DataLayer):

    @classmethod
    def get_cities(cls, stock: bool = False):
        if not stock:
            return cls.get_all(Cities)


    @classmethod
    def get_city_id(cls, city_name):
        return cls.get_one_by_criteria(Cities, "name", city_name)

    @staticmethod
    @session_decorator
    def search_city(session, city_name):
        cities = session.query(Cities).where(Cities.name.ilike(f"{city_name.title()}%")).all()
        return cities


# class

