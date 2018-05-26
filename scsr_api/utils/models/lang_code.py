from mongoengine import signals
from application import db

class lang_codeDB(db.Document):
    """ Represents the language codes and names to be used in the system.
           - The code is the ISO 639-1 code
           - The name is a dictfield in the form: {code: ['lang_name_in_code']}
               Ex:
                    {'pt':["Português"], 'en':["Portuguese"]}
    """

    code = db.StringField(db_field="db_lang_code", required=True, primary_key=True) # pylint: disable=no-member
    lang = db.DictField(db_field="db_lang_name", required=True) # pylint: disable=no-member
    in_system = db.BooleanField(db_field="in_system", required=True, default=False) # pylint: disable=no-member

    def to_obj(self):
        retorno={
            'code': self.code,
            'lang':self.lang
        }
        return retorno

    def set_system(self):
        self.in_system=True
        self.save()
