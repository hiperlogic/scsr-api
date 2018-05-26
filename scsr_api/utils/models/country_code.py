from mongoengine import signals
from application import db

class country_codeDB(db.Document):
    """ Represents the language codes and names to be used in the system.
           - The code is the ISO 3166-2 code
           - The name is a dictfield in the form: {lang_code: ['country_name_in_lang']}
               Ex:
                    {'pt':["Português"], 'en':["Portuguese"]}
    """

    code = db.StringField(db_field="db_country_code", required=True, primary_key=True)
    country = db.DictField(db_field="db_country_name", required=True)

    def to_obj(self):
        retorno={
            'code': self.code,
            'country':self.country
        }
        return retorno
