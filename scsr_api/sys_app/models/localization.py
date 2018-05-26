import json
from application import db
from user.models.user import UserDB
from utils.models.lang_code import lang_codeDB

class TextsDB(db.Document):
    """Just to store in the DB the localization data.

    
    Attributes:
        external_id {String} -- [string-code to retrieve the text]
        site_text {Dict field} -- [Dictionary containing {text_identificator :{language:text}}] 
            Ex: 
                external_id = 'title'
                text=   {
                            'pt':'Representação Estrutural Contextual Estatística em Jogos',
                            'en':'Statistical Contextual Structural Representation in Games'
                        }
                
    """

    external_id=db.StringField(db_field="external_id", required=True, primary_key=True) # pylint: disable=no-member
    text=db.DictField(db_field="site_text", required=True) # pylint: disable=no-member

class PageTextsDB(db.Document):
    """Stores the needed texts for the specified page
    
    """

    page_id = db.StringField(db_field="page_id", required="True", primary_key=True) # pylint: disable=no-member
    page_texts = db.ListField(db.ReferenceField(TextsDB), db_field="page_texts", required=True, unique=True) # pylint: disable=no-member

class TranslationsAO(object):
    """Stores  which language the system supports
    
    Arguments:
        db {[type]} -- [description]
    """

    @staticmethod
    def get_languages():
        return lang_codeDB.objects() # pylint: disable=no-member

    @staticmethod
    def get_system_languages():
        return lang_codeDB.objects.filter(in_system=True) # pylint: disable=no-member

    @staticmethod
    def has_language(codigo):
        """Returns the code or a None object.
        
        Arguments:
            codigo {string(2)} -- The language code
        
        Returns:
            SystemTranslationsObject -- A SystemTranslationsObject with the language object indicating it exists, or None if not.
        """
        the_lang=lang_codeDB.objects.filter(code=codigo).first() # pylint: disable=no-member
        return the_lang.in_system
