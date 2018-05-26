import json
from mongoengine import signals
from application import db
from uuid import uuid4
from datetime import datetime
from collections import abc

from sys_app.models.localization import TranslationsAO
from game.models.game import GameAO

class ElementAO(object):
    def __init__(self):
        self.external_id=None
        self.active=True
        self.element={}
        self.reassigned_to=None
        self.reassigned_from=[]
        self.updated=None
        self.created=None

    @staticmethod
    def from_db(db_obj):
        if(not isinstance(db_obj,ElementDB)):
            raise TypeError("ERROR: Argument is not a valid ElementDB object.")
        retorno = ElementAO()
        retorno.external_id = db_obj.external_id
        retorno.active = db_obj.active
        retorno.element = db_obj.element
        if db_obj.reassigned_to:
            retorno.reassigned_to = db_obj.reassigned_to.to_obj()
        if db_obj.reassigned_from:
            retorno.reassigned_from = [elem.to_obj() for elem in db_obj.reassigned_from]
        retorno.updated = db_obj.updated
        retorno.created = db_obj.created
        return retorno

    def __eq__(self,other):
        return self.__hash__()==other.__hash__()

    def __semi_hash__(self):
        the_str=""
        langs=list(self.element.keys())
        if langs:
            langs.sort()
            for key in langs:
                the_str+=f"{key}:{self.element[key]} - "
        the_str+=str(self.active)+" "
        elts=[elem.external_id for elem in self.reassigned_from]
        if elts:
            elts.sort()
            for elt in elts:
                the_str+=f"{elt} - "
        if self.reassigned_to:
            the_str+=self.reassigned_to.external_id+" - "
        return the_str

    def __hash__(self):
        """ Returns the hash value of the object.
            The hash value is created considering the following form:
                Starts with a DB indicating it is from database
                Get the element keys as list. It is the list of languages. Sort it
                The sorted list is used to form the string combo for each element (yes, ends with a dash space): lang+element - 
                To this string appends the active value
                Creates the string for reassigned from, using only the external_id of the elements
                The reassigned_to must be the same. This is valid only with the external_id (or else we have a recursion)
                Finally, the updated data.
        """
        the_str="AO "+self.__semi_hash__()
        return hash(the_str)

    def compare_persisted(self,db_obj):
        if not isinstance(db_obj,ElementDB):
            return False
        self_hash=hash(self.__semi_hash__())
        db_hash=hash(db_obj.__semi_hash__())
        return self_hash==db_hash


    def __update_data__(self,db_obj):
        if(not isinstance(db_obj,ElementDB)):
            raise TypeError("ERROR: Argument is not a valid ElementDB object.")
        self.external_id = db_obj.external_id
        self.active = db_obj.active
        self.element = db_obj.element
        if db_obj.reassigned_to:
            self.reassigned_to = db_obj.reassigned_to.to_obj()
        if db_obj.reassigned_from:
            self.reassigned_from = [elem.to_obj() for elem in db_obj.reassigned_from]
        self.updated = db_obj.updated

    @staticmethod
    def seek_or_create(lang,elem):
        if(not TranslationsAO.has_language(lang)):
            raise RuntimeError("ERROR: Language "+lang+" still not supported!")
        elemento = ElementDB.seek_or_create(lang,elem)
        if(not elemento):
            raise RuntimeError("ERROR: Element not present in persistence layer.")
        return elemento.to_obj()

    @staticmethod
    def search(lang,elem):
        if(not TranslationsAO.has_language(lang)):
            raise RuntimeError("ERROR: Language "+lang+" still not supported!")
        elemento = ElementDB.seek_or_create(lang,elem)
        if(not elemento):
            raise RuntimeError("ERROR: Element not created.")
        return elemento.to_obj()
        
    @staticmethod
    def suggest(lang,elem):
        return [elem.to_obj() for elem in ElementDB.suggests(lang,elem)]

    def __repr__(self):
        return f"{self.external_id}: {self.element} - active: {self.active} \n {self.reassigned_to if self.reassigned_to else ''} \n {self.reassigned_from if self.reassigned_from else ''}"

    def add_name(self,lang,name):
        """ Adds or updates the element name within the specifies language
        
        Arguments:
            lang {str[2]} -- The language code (2 characters, lower case)
            name {str} -- The name of the element (ideally in the language informed)
        """
        if(not TranslationsAO.has_language(lang)):
            raise RuntimeError("ERROR: Language "+lang+" still not supported!")
        self.element[lang]=name
        if not hasattr(self,"has_new"):
            self.has_new=set()
        self.has_new.add((lang,name))

    def was_modified(self):
        return hasattr(self,"has_new")

    def save(self):
        if not hasattr(self,"has_new"):
            return None#no changes were made. Empty objects would not be saved
        to_save=None
        if self.external_id:
            to_save=ElementDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member
            if not to_save:
                raise RuntimeError("ERROR: Unmatched object to update. Game not found in DB. External_ID: "+self.external_id)
            if not self.was_modified():
                return
            else:
                to_save.updated = datetime.utcnow()
        else:
            to_save=ElementDB()
        self.__delattr__("has_new")
        #The name can only be modified via add_name
        to_save.element=self.element
        to_save.active=self.active
        # External ID is set on the DB if a new element
        # Reassigned From and Reassigned To is not modified via AO, only via admin data. (To be coded)
        to_save.save()
        self.created=to_save.created
        self.updated=to_save.updated
        self.__update_data__(to_save)
        return self
        
    def delete(self):
        self.active=False
        el=ElementDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member
        el.active=False
        el.save()
        self.updated=el.updated
        return self

    def to_json(self):
        return { # The external_id is the key
            self.external_id:{
                "active":self.active,
                "element":self.element,
                "reassigned_to":self.reassigned_to.to_json(),
                "reassigned_from":[refrom.to_json() for refrom in self.reassigned_from]
            }
        }

    def __get_persisted__(self):
        if not self.external_id:
            return None
        return ElementDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member

class ElementDB(db.Document):
    """Class mapping the element object in the system with the element data in the database
    
        Arguments:
        db {Document} -- Derive from the Document class in MongoEngine
    
        Attributes:
        external_id {StringField} -- A string containing a uuid data representing a single element. A primary key to be provided to external applications
        active      {BooleanField} -- A boolean value indicating whether the element is active (in use/is part of computations) or not in the system.
                                    This field represents data that had identified duplicate (due to the distributiveness and concurrency of the system)
                                    A False value excludes the data to be provided to queries (such as suggestions)
        element     {DictField} --  The proper element is represented with a dictionary to provide multilang feature. The format of the data consists in the pair
                                    lang : element, like: {'pt':'personagem', 'en': 'character'}
        reassigned_to {ReferenceField(ElementDB)} -- a reference field indicating the current element is deprecated and to which one the context was reassigned
        reassigned_from {ReferenceField(ElementDB)} -- a reference field indicating that it now holds responsibility to contextualize the meaning of the former element

    """

    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    # Element field is a dictfield to provide multilang data.
    # Data form: {'lang1':'element', 'lang2':'element'}
    element = db.DictField(db_field = "element", required=True) # pylint: disable=no-member
    active = db.BooleanField(db_field = "active", default = True) # pylint: disable=no-member
    reassigned_to=db.ReferenceField("self",db_field='reassiged_to') # pylint: disable=no-member
    reassigned_from=db.ListField(db.ReferenceField('self'),db_field='reassiged_from') # pylint: disable=no-member
    updated=db.DateTimeField(db_field="updated", required=True, default=datetime.utcnow) # pylint: disable=no-member
    created=db.DateTimeField(db_field="created", required=True, default=datetime.utcnow) # pylint: disable=no-member
    
    meta = {
        "indexes": [("external_id", "active", "element")]
    }
    
    def __repr__(self):
        return f"{self.external_id}: {self.element} - active: {self.active} \n {self.reassigned_to if self.reassigned_to else ''} \n {self.reassigned_from if self.reassigned_from else ''}"

    def __eq__(self,other):
        return self.__hash__()==other.__hash__()

    def __semi_hash__(self):
        the_str=""
        langs=list(self.element.keys())
        if langs:
            langs.sort()
            for key in langs:
                the_str+=f"{key}:{self.element[key]} - "
        the_str+=str(self.active)+" "
        elts=[elem.external_id for elem in self.reassigned_from]
        if elts:
            elts.sort()
            for elt in elts:
                the_str+=f"{elt} - "
        if self.reassigned_to:
            the_str+=self.reassigned_to.external_id+" - "
        return the_str

    def __hash__(self):
        """ Returns the hash value of the object.
            The hash value is created considering the following form:
                Starts with a DB indicating it is from database
                Get the element keys as list. It is the list of languages. Sort it
                The sorted list is used to form the string combo for each element (yes, ends with a dash space): lang+element - 
                To this string appends the active value
                Creates the string for reassigned from, using only the external_id of the elements
                The reassigned_to must be the same. This is valid only with the external_id (or else we have a recursion)
                Finally, the updated data.
        """
        the_str="DB "+self.__semi_hash__()
        return hash(the_str)

    def compare_application(self,ao_obj):
        if not isinstance(ao_obj,ElementAO):
            return False
        self_hash=hash(self.__semi_hash__())
        ao_hash=hash(ao_obj.__semi_hash__())
        return self_hash==ao_hash


    def to_obj(self):
        return ElementAO.from_db(self)

    def update_element(self,lang,elem):
        """Updates the element sign for the language without performing a full scale mapping
        
        Arguments:
            lang {string(2)} -- The string representing the system language to indicate the element
            elem {string} -- The proper sign of the element
        """

        self.element[lang]=elem
        self.save()

    @staticmethod
    def reassign(current,deprecated):
        """Reassign the deprecated element to the current one. Used to maintain the semantics sanity of the system
        
            Arguments:
                current {ElementDB} -- The element that will assume the meaning
                deprecated {ElementDB} -- The element whose meaning will be transfered

            Some ground rules:
                If the element has a reassigned_to, the active field must be false.
                If the element has a reassigned_from, each element in the reassigned from list must have this element as reassigned to.
                This does not update the stored SCSR user data, but must perform recalculations on SCSR consolidated data.
                This does, however, updates the SCSR user data sent to the Frontend. The change must be highlighted and explained.
                If the user updates, the deprecated is removed and the current is added.
        """
        if((not isinstance(current,ElementDB)) or (not isinstance(deprecated,ElementDB))):
            return False
        #Set the reassigned_to
        deprecated.reassiged_to=current
        deprecated.active=False
        deprecated.save()
        #
        #Set the reassigned_from
        if(not current.reassigned_from):
            current.reassigned_from=[]
        current.reassigned_from.append(deprecated)
        current.save()
        # This is what must return
        return True


    @staticmethod
    def seek_or_create(lang,element):
        elemento=ElementDB.seek_element(lang,element)
        if(not elemento):
            elemento=ElementDB()
            elemento.element={}
            elemento.element[lang]=element
            elemento.save()
        return elemento
            

    @staticmethod
    def seek_element(lang,elem):
        return ElementDB.objects(__raw__={"element."+lang.lower():elem,"active":True}).first() # pylint: disable=no-member

    @staticmethod
    def seek(ext_id):
        return ElementDB.objects.filter(external_id=ext_id).first() # pylint: disable=no-member

    @staticmethod
    def suggests(lang,elem):
        """Returns the list of elements that contains or starts with the partial text provided in the language of the typer
        
            Arguments:
                lang {String} -- The language of the element
                elem {String} -- The partial string that the element contains
        """
        return ElementDB.objects(__raw__={"element."+lang.lower():{'$regex':elem,'$options':'i'}, "active":True}) # pylint: disable=no-member
        
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ Prior to saving the element check if all lang are supported, set the external_id

        
        Arguments:
            sender {ElementDB} -- The sender of the signal
            document {ElementDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """ With a successful save check if there is a reference element. If not, create one.
        
        Arguments:
            sender {ElementDB} -- The sender of the signal
            document {ElementDB} -- The instance of the document
        """

        refel=ElementReferenceDB.objects.filter(element=document).first() # pylint: disable=no-member
        if not refel:
            #Element just created. Create the reference for it
            ElementReferenceAO(element=document.to_obj()).save()

signals.pre_save.connect(ElementDB.pre_save, sender=ElementDB)
signals.post_save.connect(ElementDB.post_save, sender=ElementDB)

class ElementReferenceDB(db.Document):
    """ Class to perform ORM of the reference related to the element
    
        Attributes:
            element {ElementDB} -- The element the reference is related
            ref {Dict} -- The reference data. This is a dict provided with the following structure:
                {"type":[TYPE], "source":[SOURCE], "ref":[REFERENCE] (,"ambiguity":[BOOLEAN])}
                Where: 
                    TYPE assumes the values:
                        'single': for a single source, or 
                        'multi': for multiple sources
                    SOURCE refers to what is contained in the ref field and assumes the values:
                        'text': for a single text in the reference field
                        'link': for links to webpages
                        'paper': for academic reference 
                        'book': for literary reference or
                        'multi': for multiple types of references (only available if TYPE is multi)
                    REFERENCE is the reference data and it is dependant on the SOURCE in the following form: if the SOURCE is
                        'text': The Reference is a string
                        'link': The Reference is a string beginning with http:// (refers to a website)
                        'paper': The reference is a dict with the PAPER structure
                        'book': The reference is a dict with the BOOK structure
                        'multi': Each reference is a list with the reference structure
                    ambiguity is a field that can occurs in type multi. The references may provide ambiguous meaning

                The structures:
                    PAPER: {"author":[AUTHOR],"title":[TITLE],"published":[YEAR],"source":[EVENT/JOURNAL] (,"doi":[DOI], "coauthors":[[AUTHORS]])}
                        Excluding YEAR that must be a valid int, all other fields are strings and coauthors, a list of string
                    BOOK: {"author":[AUTHOR],"title":[TITLE],"published":[YEAR],"publisher":[PUBLISHER], "isbn":[ISBN] (,"coauthors":[[AUTHORS]], "page":[PAGE])}
                        Excluding YEAR and PAGE that must be a valid int, all other fields are strings and coauthors, a list of string
                    REF: {"type":[TYPE], "ref":[REFERENCE]}
                        The REF type is a subset of REFERENCE type that excludes the multi type. 

        Methods:
            to_obj {ElementReferenceAO} --
    """

    element = db.ReferenceField(ElementDB,db_field="element",primary_key=True, required=True) # pylint: disable=no-member
    reference = db.DictField(db_field="reference", required=True) # pylint: disable=no-member

    def to_obj(self):
        return ElementReferenceAO.from_db(self)

class ElementReferenceAO(object):
    def __init__(self, element=None, reference=None):
        if element:
            if not isinstance(element,ElementAO):
                raise TypeError("ERROR: Not a valid ElementDB object to be referenced")
        self.element=element
        if not reference:
            reference={"type":"single", "source":"text", "ref":"No Reference"}
        self.reference=reference

    @staticmethod
    def from_db(db_obj):
        if not isinstance(db_obj,ElementReferenceDB):
            raise TypeError("ERROR: Argument is not a valid ElementReferenceDB object")
        return ElementReferenceAO(db_obj.element.to_obj(),db_obj.reference)

    def set_element(self,element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Not a valid ElementDB object to be referenced")
        self.element=element
    
    def set_reference(self,ref):
        if not isinstance(ref,dict):
            raise TypeError("ERROR: Reference must be a dict with the keys (and possible values): type(single,multi), source(text,link,paper), ref(the reference)")
        s=ref.get("source")
        t=ref.get("type")
        r=ref.get("ref")
        if not (s and r and t):
            raise TypeError("ERROR: Reference must be a dict with the keys (and possible values): type(single,multi), source(text,link,paper), ref(the reference)")
        if s=="multi" and t!="multi":
            raise RuntimeError("ERROR: Multiple Source is only possible with type multi")
        self.reference=ref

    def save(self):
        if(not self.element):
            raise RuntimeError("ERROR: Cannot create an element reference to a None.")
        db_obj=ElementReferenceDB()
        el_db=ElementDB.objects.filter(external_id=self.element.external_id).first() # pylint: disable=no-member
        db_obj.element=el_db
        db_obj.reference=self.reference
        db_obj.save()

    @staticmethod
    def get_reference(element):
        if not isinstance(element,ElementAO):
            raise TypeError("Error: Trying to get a reference of a not ElementAO object")
        el_db=ElementDB.objects.filter(external_id=element.external_id).first() # pylint: disable=no-member
        the_ret=ElementReferenceDB.objects.filter(element=el_db).first() # pylint: disable=no-member
        if(not the_ret):
            raise RuntimeError("Error Valid Element Object does not possess reference")
        return the_ret.to_obj()
    
    @staticmethod
    def get_reference_sources():
        return {
            'text': "a single text in the reference field",
            'link': "links to webpages",
            'paper': "academic reference ",
            'book': "literary reference or",
            'multi': "multiple types of references (only available if TYPE is multi)"
        }

    @staticmethod
    def get_reference_types():
        return {
            "single": "a single source of information",
            "multi":"multiple sources or reference"
        }

    @staticmethod
    def get_sources_structure():
        return {
            'text': "A single string",
            'link': "http://the_link.com",
            'paper': '{"author":[AUTHOR],"title":[TITLE],"published":[YEAR],"source":[EVENT/JOURNAL] (,"doi":[DOI], "coauthors":[[AUTHORS]])} "',
            'book': '{"author":[AUTHOR],"title":[TITLE],"published":[YEAR],"publisher":[PUBLISHER], "isbn":[ISBN] (,"coauthors":[[AUTHORS]], "page":[PAGE])}',
            'multi': '{"type":[TYPE], "ref":[REFERENCE]} (type refers to source type. excludes the multi, ref is the related structured data)'
        }


class ElementGameMappingDB(db.Document):
    """ Class to map the games that were assigned to the elements.
        Data in this collection are just provided when SCSR is saved.
        If SCSR is modified and the element removed, this association maintains.
        This association means that there are (or were) interpretation that the element was associated with the game.
        This collection helps to get the game and assess how it was interpreted.    
    """

    element = db.ReferenceField(ElementDB, db_field="element", required=True, primary_key=True) # pylint: disable=no-member
    #After the system starts, each new element added will have a game associated. Only prior there will be the pre-recorded elements.
    games = db.DictField(db_field="games") # pylint: disable=no-member

    @staticmethod
    def get_games(element):
        """ get the games associated with the provided element
        
        Arguments:
            element {ElementAO} -- The Application Object representing the element.
        
        Raises:
            TypeError -- If the argument is not a valid ApplicationObject
            RuntimeError -- If the argument is valid, but represents no valid data in the collection
        
        Returns:
            List -- List of GameAO objects associated with this element.
        """

        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument is not a valid ElementAO object.")
        elementdb=ElementDB.objects.filter(external_id=element.external_id).first() # pylint: disable=no-member
        if not elementdb:
            raise RuntimeError("ERROR: Could not retrieve data for the element: "+element.external_id)
        return [game.to_obj() for game in elementdb.games]

class ElementGameMappingAO(abc.MutableSet):
    def __init__(self, games=(), element=""):
        self.games = set(games)

        self.element = element

        self.composition = []

    def __contains__(self, other):
        return other in self.games

    def is_composite(self):
        return self.composition

    def __iter__(self):
        return iter(self.games)

    def __len__(self):
        return len(self.games)

    def __or__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno=self.__class__(self.games | other.games, element=self.element)
        retorno.composition=["or",(self.composition if self.is_composite else self.element,
                            other.composition if other.is_composite else other.element)]
        return retorno

    def __and__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games & other.games, element=self.element)
        retorno.composition=["and",(self.composition if self.is_composite else self.element,
                            other.composition if other.is_composite else other.element)]
        return retorno

    def __xor__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games ^ other.games, element=self.element)
        retorno.composition=["xor",(self.composition if self.is_composite else self.element,
                            other.composition if other.is_composite else other.element)]
        return retorno

    def __sub__(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games - other.games, element=self.element)
        retorno.composition=["difference",(self.composition if self.is_composite else self.element,
                            other.composition if other.is_composite else other.element)]
        return retorno

    def add(self, game):
        if not isinstance(game,GameAO):
            raise TypeError("Game is not a valid GameAO object")
        self.games.add(game)

    def discard(self, game):
        if not isinstance(game,GameAO):
            raise TypeError("Game is not a valid GameAO object")
        self.games.discard(game)

    def __json__(self):
        return {game:1  for game in self.games }

    def __repr__(self):
        base = f"{self.element}: {self.games}"
        if self.composition:
            base += f"\nComposition: {self.composition}"
        return base

    def save(self):
        if not isinstance(self.element,ElementAO):
            raise TypeError("Classificator element not a valid ElementAO object.")
        for game in self.games:
            if not isinstance(game,GameAO):
                raise TypeError("Attempting to save a non GameAO object")
        if self.is_composite():
            raise RuntimeError("Attempting to persist a composite object. Operation not allowed")
        # This data can be save only and if only t is not a composite operand. That means, there were games added to the genre.
        #first: Get the elementdb via element external_id. The element must exist!
        theElDB=ElementDB.objects.filter(external_id=self.element.external_id).first() # pylint: disable=no-member
        if not theElDB:
            raise RuntimeError("ERROR: No Element was found in the persistence layer. ID: "+self.element.external_id)
        #now, get the current db object
        theDB=ElementGameMappingDB.objects.filter(element=theElDB).first() # pylint: disable=no-member
        if not theDB:
            raise RuntimeError("ERROR: Related GameElementMapping not found in the persistent layer.")
        theDB.games=self.__json__()

    for method in ['clear', 'copy', 'difference', 'difference_update', 'discard', 'intersection', 'intersection_update', 'isdisjoint', 'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference', 'symmetric_difference_update', 'union', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.games, method)(*((other,) if other else ()) ) ) (method)
