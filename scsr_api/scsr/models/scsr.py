from mongoengine import signals
from uuid import uuid4
from datetime import datetime, timedelta
from collections import abc

import copy
from user.models.user import UserDB, UserAO
from game.models.game import GameDB, GameAO
from game.models.genre import GenreDB, GenreAO
from game.models.user_game_genre import GamesGenresDB, GamesGenresAO

from scsr.models.elements import ElementAO

from scsr.models.persuasive_function import PersuasiveFunctionDB, PersuasiveFunctionAO
from scsr.models.aesthetic_function import AestheticFunctionDB, AestheticFunctionAO
from scsr.models.orchestration_function import OrchestrationFunctionDB, OrchestrationFunctionAO
from scsr.models.reification_function import ReificationFunctionDB, ReificationFunctionAO

from application import db
from application import the_log


class ScsrDiffAO():
    def __init__(self):
        self.external_id=None
        self.date_modified=None
        coded_scsr=None

    @staticmethod
    def from_db(db_obj):
        retorno=ScsrDiffAO()
        retorno.external_id=db_obj.external_id
        retorno.date_modified=db_obj.date_modified
        retorno.coded_scsr={
            "persuasive":{
                "interactivity":db_obj.coded_scsr['persuasive']['interactivity'].to_obj(),
                "gamefication":db_obj.coded_scsr['persuasive']['gamefication'].to_obj(),
                "ludic":db_obj.coded_scsr['persuasive']['ludic'].to_obj(),
                },
            "aesthetic":{
                "interactivity":db_obj.coded_scsr['aesthetic']['interactivity'].to_obj(),
                "ludic":db_obj.coded_scsr['aesthetic']['ludic'].to_obj(),
                },
            "orchestration":{
                "interactivity":db_obj.coded_scsr['orchestration']['interactivity'].to_obj(),
                "gamefication":db_obj.coded_scsr['orchestration']['gamefication'].to_obj(),
                "mechanical":db_obj.coded_scsr['orchestration']['mechanical'].to_obj(),
                },
            "reification":{
                "interactivity":db_obj.coded_scsr['reification']['interactivity'].to_obj(),
                "mechanical":db_obj.coded_scsr['reification']['mechanical'].to_obj(),
                "device":db_obj.coded_scsr['reification']['device'].to_obj(),
                }
        }
        return retorno

    def to_json(self):
        retorno={
            "external_id": self.external_id,
            "date_modified": self.date_modified, 
            "coded_scsr" : {
                "persuasive":{
                    "interactivity":self.coded_scsr['persuasive']['interactivity'].to_json(),
                    "gamefication":self.coded_scsr['persuasive']['gamefication'].to_json(),
                    "ludic":self.coded_scsr['persuasive']['ludic'].to_json(),
                    },
                "aesthetic":{
                    "interactivity":self.coded_scsr['aesthetic']['interactivity'].to_json(),
                    "ludic":self.coded_scsr['aesthetic']['ludic'].to_json(),
                    },
                "orchestration":{
                    "interactivity":self.coded_scsr['orchestration']['interactivity'].to_json(),
                    "gamefication":self.coded_scsr['orchestration']['gamefication'].to_json(),
                    "mechanical":self.coded_scsr['orchestration']['mechanical'].to_json(),
                    },
                "reification":{
                    "interactivity":self.coded_scsr['reification']['interactivity'].to_json(),
                    "mechanical":self.coded_scsr['reification']['mechanical'].to_json(),
                    "device":self.coded_scsr['reification']['device'].to_json(),
                    }
                }
        }
        return retorno

class ScsrDiffDB(db.Document):
    """
        The scsr mods class represents a modification made to a scsr.
        The dictionary referencing the element contains the functions and behaviors as the normal SCSR, but with the added and removed list of elements.
        This provides a method to track the scsr evolution within time.
        The coded_scsr is a dict representing the difference
        The external_id in the return refers to the diff external id.
        The coded scsr is of the form:
        {
            persuasive: persuasive_diff
            aesthetic: aesthetic_diff
            orchestration: orchestration_diff
            reification: reification_diff
        }
        With each diff representing a persisted object of the respective function.
    """
    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    date_modified = db.DateTimeField(db_field="date_modified", required=True, default=datetime.utcnow) # pylint: disable=no-member
    coded_scsr = db.DictField(db_field="coded_scsr", required = True, default={}) # pylint: disable=no-member

    def to_obj(self):
        return ScsrDiffAO.from_db(self)

    def to_json(self):
        return ScsrDiffAO.from_db(self).to_json()

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ Prior to saving the scsrdiff, guarantees its consistencies and check the external_id
        
        Arguments:
            sender {scsrDiffDB} -- The sender of the signal
            document {scsrDiffDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

    


signals.pre_save.connect(ScsrDiffDB.pre_save, sender=ScsrDiffDB)


class ScsrAO(abc.MutableSet):
    """ TODO: Redefine the DOCSTRING
    """

    def __init__(self, persuasive_=None, aesthetic_=None, orchestration_=None, reification_=None):
        if persuasive_ and (not isinstance(persuasive_,PersuasiveFunctionAO)):
            raise TypeError("ERROR: Parameter is not a valid PersuasiveFunctionAO object")
        if aesthetic_ and (not isinstance(aesthetic_,AestheticFunctionAO)):
            raise TypeError("ERROR: Parameter is not a valid AestheticFunctionAO object")
        if orchestration_ and (not isinstance(orchestration_,OrchestrationFunctionAO)):
            raise TypeError("ERROR: Parameter is not a valid OrchestrationFunctionAO object")
        if reification_ and (not isinstance(reification_,ReificationFunctionAO)):
            raise TypeError("ERROR: Parameter is not a valid ReificationFunctionAO object")
        self.external_id = None
        self.user = None
        self.game = None
        #create empty functions to be able to operate
        self.persuasive_function = persuasive_ if persuasive_ else PersuasiveFunctionAO()
        self.aesthetic_function = aesthetic_ if aesthetic_ else AestheticFunctionAO()
        self.orchestration_function = orchestration_ if orchestration_ else OrchestrationFunctionAO()
        self.reification_function = reification_ if reification_ else ReificationFunctionAO()
        self.history = []
        self.date_creation = None
        self.date_modified = None
        self.is_composite=False
        self.unassigned = []

    #TODO: TEST
    @staticmethod
    def from_db(scsr):
        retorno = ScsrAO()
        if not isinstance(scsr,ScsrDB):
            raise TypeError("ERROR: Assigning a non SCSR object to SCSR application object")
        retorno.external_id=scsr.external_id
        retorno.user=scsr.user.to_obj()
        retorno.game=scsr.game.to_obj()
        retorno.persuasive_function=scsr.persuasive_function.to_obj()
        retorno.aesthetic_function=scsr.aesthetic_function.to_obj()
        retorno.orchestration_function=scsr.orchestration_function.to_obj()
        retorno.reification_function=scsr.reification_function.to_obj()
        retorno.history=[diff.to_obj() for diff in scsr.history]
        retorno.date_creation=scsr.date_creation
        retorno.date_modified=scsr.date_modified
        return retorno

    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno="\nUser: "+self.user
        retorno="\Game: "+self.game
        retorno+="\n"+"#"*50+"\nPersuasive: \n"+self.persuasive_function.__repr__()
        retorno+="\n"+"#"*50+"\nAesthetic: \n"+self.aesthetic_function.__repr__()
        retorno+="\n"+"#"*50+"\nOrchestration: \n"+self.orchestration_function.__repr__()
        retorno+="\n"+"#"*50+"\nReificaton: \n"+self.reification_function.__repr__()
        return retorno

    def __semi_hash__(self):
        retorno = self.external_id+"-"+self.user.__semi_hash__()+self.game.__semi_hash__()+self.persuasive_function.__semi_hash__()
        retorno = retorno + self.aesthetic_function.__semi_hash__() + self.orchestration_function.__semi_hash__()
        retorno = retorno + self.reification_function.__semi_hash__() + self.date_creation + self.date_modified
        return retorno

    def __hash__(self):
        return hash(self.__semi_hash__()+"AO")


    #TODO: TEST
    def revert_diff(self,difdata):
        """ Reverts current structure with diff data. (maintaining the diff_data structure)
        
        Arguments:
            difdata {dict} -- The dictionary of diff data. The diffdata is composed of the element as key and 1, if added or -1, if removed.
        
        Returns:
            BehaviorAO -- the same object, with the elements altered.
        """
        #check diff structure:
        if not isinstance(difdata,ScsrDiffAO):
            return self
        self.persuasive_function=self.persuasive_function.revert_diff(difdata.coded_scsr["persuasive"])
        self.aesthetic_function=self.aesthetic_function.revert_diff(difdata.coded_scsr["aesthetic"])
        self.orchestration_function=self.orchestration_function.revert_diff(difdata.coded_scsr["orchestration"])
        self.reification_function=self.reification_function.revert_diff(difdata.coded_scsr["reification"])
        return self

    def reset(self):
        #only maintains diffdata
        self.persuasive_function.reset()
        self.orchestration_function.reset()
        self.aesthetic_function.reset()
        self.reification_function.reset()
        self.save()
        return self

    def __contains__(self, element):
        inpf = element in self.persuasive_function
        inaf = element in self.aesthetic_function
        inof = element in self.orchestration_function
        inrf = element in self.reification_function
        return inpf or inaf or inof or inrf

    #TODO: TEST
    def __iter__(self):
        #will iter in all elements of the functions
        elements1=[el for el in self.persuasive_function.elements]
        elements2=[el for el in self.aesthetic_function.elements]
        elements3=[el for el in self.orchestration_function.elements]
        elements4=[el for el in self.reification_function.elements]
        return iter(elements1+elements2+elements3+elements4)

    #TODO: TEST
    def __len__(self):
        #length is the sum of all the lengths
        return len(self.persuasive_function)+len(self.aesthetic_function)+len(self.orchestration_function)+len(self.reification_function)


    #TODO: TEST
    def __or__(self, other):
        is_composite=False
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.game==other.game:
            is_composite=True #composed type cannot be saved!
        por=self.persuasive_function | other.persuasive_function
        aor=self.aesthetic_function | other.aesthetic_function
        oor=self.orchestration_function | other.orchestration_function
        ror=self.reification_function | other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno

    #TODO: TEST
    def __and__(self, other):
        is_composite=False
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.game==other.game:
            is_composite=True #composed type cannot be saved!
        por=self.persuasive_function & other.persuasive_function
        aor=self.aesthetic_function & other.aesthetic_function
        oor=self.orchestration_function & other.orchestration_function
        ror=self.reification_function & other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno


    #TODO: TEST
    def __xor__(self, other):
        is_composite=False
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.game==other.game:
            is_composite=True #composed type cannot be saved!
        por=self.persuasive_function ^ other.persuasive_function
        aor=self.aesthetic_function ^ other.aesthetic_function
        oor=self.orchestration_function ^ other.orchestration_function
        ror=self.reification_function ^ other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno

    #TODO: TEST
    def __sub__(self,other):
        is_composite=False
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.game==other.game:
            is_composite=True #composed type cannot be saved!
        por=self.persuasive_function - other.persuasive_function
        aor=self.aesthetic_function - other.aesthetic_function
        oor=self.orchestration_function - other.orchestration_function
        ror=self.reification_function - other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno

    #TODO: TEST
    #__radd__ can add BehaviorAO+0, that's why we check the validity. If valid it must be a BehaviorAI
    # if not valid, then create an empty BehaviorAO and perform the add
    def __radd__(self,other):
        is_composite=False
        if other:
            if not isinstance(other,ScsrAO):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
            if not self.game==other.game:
                is_composite=True #composed type cannot be saved!
        else:
            other=ScsrAO()
        por=self.persuasive_function + other.persuasive_function
        aor=self.aesthetic_function + other.aesthetic_function
        oor=self.orchestration_function + other.orchestration_function
        ror=self.reification_function + other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno

    #TODO: TEST
    # Unlike __radd__, where the other can be 0 (used for sum), __add__ demands an argument.
    def __add__(self,other):
        is_composite=False
        if other:
            if not isinstance(other, ScsrAO):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
            if not self.game==other.game:
                is_composite=True #composed type cannot be saved!
        else:
            other=ScsrAO()
        por=self.persuasive_function + other.persuasive_function
        aor=self.aesthetic_function + other.aesthetic_function
        oor=self.orchestration_function + other.orchestration_function
        ror=self.reification_function + other.reification_function
        retorno=self.__class__(por,aor,oor,ror)
        retorno.is_composite=is_composite
        if not is_composite:
            retorno.game=self.game
        if self.user == other.user:
            retorno.user=self.user
        return retorno


    #TODO: TEST
    def diff(self,other):
        if not isinstance(other, ScsrAO):
            raise TypeError("ERROR: Trying to diff two different, non related objects")
        return {
            "persuasive":self.persuasive_function.diff(other.persuasive_function),
            "aesthetic":self.aesthetic_function.diff(other.aesthetic_function),
            "orchestration":self.orchestration_function.diff(other.orchestration_function),
            "reification":self.reification_function.diff(other.reification_function)
        }


    #TODO: TEST
    @staticmethod
    def s_accounted_diff(one,others):
        """ Performs a diff with each behavior object in the list returning the accountant concerning how much an element was added or removed
        
        Arguments:
            others {list(BehaviorAO)} -- List of BehaviorAO elements
        
        Raises:
            TypeError -- If any element is not a BehaviorAO
        
        Returns:
            Dict -- A Dictionary with two lists: added, with the account of added elements, removed: with the account of removed elements (or absent from the left operand).
        """

        if not isinstance(one, ScsrAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        if isinstance(others,list):
            for other in others:
                if not isinstance(other,ScsrAO):
                    raise TypeError("ERROR: Trying to sum two different, non related objects")
            accum=sum(others)
        else:
            accum=others
        return {
            "persuasive":one.persuasive_function.diff(accum.persuasive_function),
            "aesthetic":one.aesthetic_function.diff(accum.aesthetic_function),
            "orchestration":one.orchestration_function.diff(accum.orchestration_function),
            "reification":one.reification_function.diff(accum.reification_function)
        }
        

    #TODO: TEST
    @staticmethod
    def s_diff(one,other):
        if not isinstance(other,ScsrAO) or not isinstance(one,ScsrAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        return {
            "persuasive":one.persuasive_function.diff(other.persuasive_function),
            "aesthetic":one.aesthetic_function.diff(other.aesthetic_function),
            "orchestration":one.orchestration_function.diff(other.orchestration_function),
            "reification":one.reification_function.diff(other.reification_function)
        }


    #TODO: TEST
    def add(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        self.unassigned.append(element)


    #TODO: TEST
    def discard(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        #it uses only ther external_id for the element data.
        self.unassigned.remove(element)
        #discard removes all occurrences of the element
        self.persuasive_function.discard(element)
        self.aesthetic_function.discard(element)
        self.orchestration_function.discard(element)
        self.reification_function.discard(element)

    #TODO: TEST
    def to_json(self):
        return {
            "external_id": self.external_id,
            "user": self.user.to_json(),
            "game": self.game.to_json(),
            "persuasive_function": self.persuasive_function.to_json(),
            "aesthetic_function": self.aesthetic_function.to_json(),
            "orchestration_function": self.orchestration_function.to_json(),
            "reification_function": self.reification_function.to_json(),
            "history":[dif.to_json() for dif in self.history],
            "created":self.date_creation,
            "modified": self.date_modified
        }


    #TODO: TEST
    @staticmethod
    def get_scsr(external_id_):
        if not isinstance(external_id_,str):
            raise TypeError("ERROR: Parameter is not a string! Definitively not a valid key.")
        db_obj=ScsrDB.objects.filter(external_id=external_id_).first() # pylint: disable=no-member
        if not db_obj:
            raise RuntimeError("Error: No persistence data found for id: "+external_id_)
        return db_obj.to_obj()

    #TODO: TEST
    @staticmethod
    def create_scsr(game,user):
        if not isinstance(game,GameAO):
            raise TypeError("ERROR: Argument is not a valid GameAO object")
        if not isinstance(user,UserAO):
            raise TypeError("ERROR: Argument is not a valid GameAO object")
        the_scsr=ScsrDB.__create_persistence__(game.__get_persisted__(),user.__get_persisted__())
        return the_scsr.to_obj()


    #TODO: TEST
    def check_save(self):
        if not self.external_id:
            return RuntimeError,"ERROR: Function was not properly created or is an operand!"
            
        if not self.game:
            return RuntimeError,"ERROR: Function was not properly created or is an operand! No game assigned"

        if not self.user:
            return RuntimeError,"ERROR: Function was not properly created or is an operand! No user assigned"

        if len(self.unassigned)>0:
            return RuntimeError,"ERROR: Function must not have unassigned elements!"

        if self.is_composite:
            return TypeError, "ERROR: Cannot save a composite data"
        return None, ""

    #TODO: TEST
    def save(self):
        """ Persists the persuasive function data.
            This persistence is given the following form:
            1 - The function must not have unassigned elements
            2 - Each behavior is saved. If one incurs error, the others are not saved. the function is not saved.
                2.1 - If behaviors are saved, and error occurs afterwards, ok. The behavior data persistence is valid, but the function is not.
            3 - The function is saved.
        
        Raises:
            TypeError -- Behavior must have the type defined and of specific value
            TypeError -- All objects in the set must be of ElementAO type and persisted. I.e.: Have a valid external_id
        """
        saved=None
        errorType,msg = self.check_save()
        if errorType:
            raise errorType(msg)
        pers=self.persuasive_function
        aest=self.aesthetic_function
        orch=self.orchestration_function
        reif=self.reification_function
        try:
            #save the behaviors
            self.persuasive_function.save()
            self.aesthetic_function.save()
            self.orchestration_function.save()
            self.reification_function.save()
        except:
            if self.persuasive_function!=pers:
                self.persuasive_function=pers
            if self.aesthetic_function!=aest:
                self.aesthetic_function=aest
            if self.orchestration_function!=orch:
                self.orchestration_function=orch
            if self.reification_function!=reif:
                self.reification_function=reif
            raise RuntimeError("ERROR: Some of the  functions  were not saved. ")
        #try saving the function
        try:
            saved=PersuasiveFunctionDB.__persist__(self)
        except:
            raise RuntimeError("ERROR: Not able to save the SCSR: "+self.external_id)
        if(saved):
            self.history=[the_diff.to_obj() for the_diff in saved.history]
    
    #TODO: TEST
    def copy(self):
        to_ret=ScsrAO(self.persuasive_function.copy(),self.aesthetic_function.copy(), self.orchestration_function.copy(), self.reification_function.copy())
        return to_ret

    #TODO: TEST
    def difference(self,other):
        if not isinstance(other, ScsrAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        retorno=self ^ other
        retorno=retorno & self
        return retorno

    #TODO: TEST
    def intersection(self,other):
        if not isinstance(other, ScsrAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        return self & other
    
    #TODO: TEST
    def union(self,other):
        if not isinstance(other, ScsrAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        return self | other

        


    #TODO: TEST
    def symmetric_difference(self,other):
        if not isinstance(other, ScsrAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        retorno=self ^ other
        return retorno

    for method in ['clear', 'isdisjoint', 'issubset', 'issuperset', 'difference_update', 'intersection_update', 'symmetric_difference_update', 'pop', 'remove', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.elements, method)(*((other,) if other else ()) ) ) (method)

        

"""The scsr class represents the understanding of the game within the representational structure.
    It has one opcional field that relates ti the user. If not set, the scsr represents the game scsr and must be unique.
    This means, for a game there must not exist more than one scsr without a user and there must always have one.
    If there is a game, there is one and only one scsr for that game that have no user assigned.
    The fields are:
        external_id - unique reference field to be sent to the client
        game - the game this scsr relates to
        user - the user that proposed this represetation. If absent, it is the game overall representation
        Persuasive Function  (elements that were assigned to this role)
        Aesthetic Function  (elements that were assigned to this role)
        Orchestration Function  (elements that were assigned to this role)
        Reification Function  (elements that were assigned to this role)
        modifications (the list of modifications to the scsr)
        date_creation (date the representation was first created)
        date_modified (date the representation was last modified)

    The modifications are mandatory and the very first modificacions is the scsr itself as saved for the first time.

"""

class ScsrDB(db.Document):
    """ Class for collection object representing the SCSR. Its only responsibility is to persist the data and retrieve the data from the collection.
        In the save, the current diff is propagated to the functions to compute the current state.
        Every other responsibility is in the Application Object.
    
        Attributes:
            external_id -- String - The primary key to be unveiled to the user
            user -- the UserDB reference object. The responsible for the representation
            game -- the GameDB object referring to the game whose structure represents
            persuasive_function -- the PersuasiveFunctionDB reference, representing the set of behaviors intended to/realized as persuasion methods or roles in/by the player
            aesthetic_function -- the AestheticFunctionDB reference, representing the set of behaviors intended to/realized as aesthetic methods or roles in/by the player
            orchestration_function -- the OrchestrationFunctionDB reference, representing the set of behaviors intended to/realized as orchestration methods or roles in/by the player
            reification_function -- the ReificationFunctionDB reference, representing the set of behaviors intended to/realized as reification methods or roles in/by the player
            history -- The list of ScsrDiff objects representing the history of changes in the structural representation
            date_creation -- The date of the creation of this representation
            date_modified -- The date of the last modification
    """

    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    user = db.ReferenceField(UserDB, db_field="user") # pylint: disable=no-member
    game = db.ReferenceField(GameDB, db_field="game", required=True) # pylint: disable=no-member
    persuasive_function = db.ReferenceField(PersuasiveFunctionDB, db_field="persuasive", required=True) # pylint: disable=no-member
    aesthetic_function = db.ReferenceField(AestheticFunctionDB, db_field="aesthetic", required=True) # pylint: disable=no-member
    orchestration_function = db.ReferenceField(OrchestrationFunctionDB, db_field="orchestration", required=True) # pylint: disable=no-member
    reification_function = db.ReferenceField(ReificationFunctionDB, db_field="reification", required=True) # pylint: disable=no-member
    history = db.ListField(db.ReferenceField(ScsrDiffDB), db_field="history", required = True) # pylint: disable=no-member
    date_creation = db.DateTimeField(db_field="date_creation", required=True, default=datetime.utcnow) # pylint: disable=no-member
    date_modified = db.DateTimeField(db_field="date_modified", required=True, default=datetime.utcnow) # pylint: disable=no-member

    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno="\nUser: "+self.user
        retorno="\Game: "+self.game
        retorno+="\n"+"#"*50+"\nPersuasive: \n"+self.persuasive_function.__repr__()
        retorno+="\n"+"#"*50+"\nAesthetic: \n"+self.aesthetic_function.__repr__()
        retorno+="\n"+"#"*50+"\nOrchestration: \n"+self.orchestration_function.__repr__()
        retorno+="\n"+"#"*50+"\nReificaton: \n"+self.reification_function.__repr__()
        return retorno

    def __semi_hash__(self):
        retorno = self.external_id+"-"+self.user.__semi_hash__()+self.game.__semi_hash__()+self.persuasive_function.__semi_hash__()
        retorno = retorno + self.aesthetic_function.__semi_hash__() + self.orchestration_function.__semi_hash__()
        retorno = retorno + self.reification_function.__semi_hash__() + self.date_creation + self.date_modified
        return retorno

    def __hash__(self):
        return hash(self.__semi_hash__()+"DB")

    def to_obj(self):
        return ScsrAO.from_db(self)

    @staticmethod
    def __create_persistence__(game,user):
        if not isinstance(game,GameDB):
            raise TypeError("ERROR: Argument is not a valid GameDB object")
        if not isinstance(user,UserDB):
            raise TypeError("ERROR: Argument is not a valid UserDB object")
        to_persist=ScsrDB()
        to_persist.user=user
        to_persist.game=game
        to_persist.persuasive_function=PersuasiveFunctionDB.__create_persistence__()
        to_persist.aesthetic_function=AestheticFunctionDB.__create_persistence__()
        to_persist.orchestration_function=OrchestrationFunctionDB.__create_persistence__()
        to_persist.reification_function=ReificationFunctionDB.__create_persistence__()
        history=ScsrDiffDB()
        history.coded_scsr={
            "persuasive": {
                "interactivity":to_persist.persuasive_function.interactivity.diffdata[-1],
                "gamefication":to_persist.persuasive_function.gamefication.diffdata[-1],
                "ludic":to_persist.persuasive_function.ludic.diffdata[-1]
                },
            "aesthetic": {
                "interactivity":to_persist.aesthetic_function.interactivity.diffdata[-1],
                "ludic":to_persist.aesthetic_function.ludic.diffdata[-1]
                },
            "orchestration": {
                "interactivity":to_persist.orchestration_function.interactivity.diffdata[-1],
                "gamefication":to_persist.orchestration_function.gamefication.diffdata[-1],
                "mechanical":to_persist.orchestration_function.mechanical.diffdata[-1]
                },
            "reification": {
                "interactivity":to_persist.reification_function.interactivity.diffdata[-1],
                "mechanical":to_persist.reification_function.mechanical.diffdata[-1],
                "device":to_persist.reification_function.device.diffdata[-1]
                }
            }
        history.save()
        to_persist.history.append(history)
        to_persist.save()
        return to_persist

    #TODO: Verifiy
    @staticmethod
    def __persist__(scao):
        if not isinstance(scao,ScsrAO):
            raise TypeError("ERROR: Argument is not a valid ScsrAO object.")
        #get the DB object of the function
        to_save=ScsrDB.objects.filter(external_id=scao.external_id).first() # pylint: disable=no-member
        if not to_save:
            raise RuntimeError("ERROR: Unable to retrieve reference to persist - ScsrDB - "+scao.external_id)
        #Behavior objects already saved. Just retrieve the DB reference from them
        pfdb=PersuasiveFunctionDB.objects.filter(external_id=scao.persuasive_function.external_id).first() # pylint: disable=no-member
        afdb=AestheticFunctionDB.objects.filter(external_id=scao.aesthetic_function.external_id).first() # pylint: disable=no-member
        ofdb=OrchestrationFunctionDB.objects.filter(external_id=scao.orchestration_function.external_id).first() # pylint: disable=no-member
        rfdb=ReificationFunctionDB.objects.filter(external_id=scao.reification_function.external_id).first() # pylint: disable=no-member
        to_save.persuasive_function=pfdb
        to_save.aesthetic_function=afdb
        to_save.orchestration_function=ofdb
        to_save.reification_function=rfdb
        to_save.date_modified=datetime.utcnow()
        history=ScsrDiffDB()
        history.coded_scsr={
            "persuasive": {
                "interactivity":to_save.persuasive_function.interactivity.diffdata[-1],
                "gamefication":to_save.persuasive_function.gamefication.diffdata[-1],
                "ludic":to_save.persuasive_function.ludic.diffdata[-1]
                },
            "aesthetic": {
                "interactivity":to_save.aesthetic_function.interactivity.diffdata[-1],
                "ludic":to_save.aesthetic_function.ludic.diffdata[-1]
                },
            "orchestration": {
                "interactivity":to_save.orchestration_function.interactivity.diffdata[-1],
                "gamefication":to_save.orchestration_function.gamefication.diffdata[-1],
                "mechanical":to_save.orchestration_function.mechanical.diffdata[-1]
                },
            "reification": {
                "interactivity":to_save.reification_function.interactivity.diffdata[-1],
                "mechanical":to_save.reification_function.mechanical.diffdata[-1],
                "device":to_save.reification_function.device.diffdata[-1]
                }
            }
        history.save()
        to_save.history.append(history)
        try:
            to_save.save()
        except:
            the_log.log("ERROR: Scsr not persisted in _persist_.")
        finally:
            return to_save

    @staticmethod
    def get_scsr(eid):
        if not isinstance(eid,str):
            raise TypeError("ERROR: Invalid type for the identification data.")
        dbdata = ScsrDB.objects.filter(external_id=eid).first() # pylint: disable=no-member
        if (not dbdata) or (not dbdata.external_id==eid):
            raise RuntimeError("ERROR: Persistent Data not Found or Mismatched.")
        return dbdata

    """ get_scsr_list_by_game - Returns a list of scsr data for the game object passed as parameter
    
    Raises:
        TypeError -- [description]
        RuntimeError -- [description]
    
    Returns:
        [type] -- [description]
    """

    @staticmethod
    def get_scsr_list_by_game(gdbo):
        if not isinstance(gdbo,GameDB):
            raise TypeError("ERROR: Invalid type for the game  data.")
        dbdata = ScsrDB.objects.filter(game=gdbo) # pylint: disable=no-member
        if (not dbdata):
            raise RuntimeError("ERROR: Persistent Data not Found or Mismatched.")
        return dbdata

    @staticmethod
    def get_scsr_list_by_user(udbo):
        if not isinstance(udbo,UserDB):
            raise TypeError("ERROR: Invalid type for the game  data.")
        dbdata = ScsrDB.objects.filter(user=udbo) # pylint: disable=no-member
        if (not dbdata):
            raise RuntimeError("ERROR: Persistent Data not Found or Mismatched.")
        return dbdata

    @staticmethod
    def get_scsr_list_by_game_and_users(gdbo, udbol):
        if not isinstance(gdbo,GameDB):
            raise TypeError("ERROR: Invalid type for the game  data.")
        for udbo in udbol:
            if not isinstance(udbo,UserDB):
                raise TypeError("ERROR: Invalid type for the game  data.")
        dbdata = ScsrDB.objects.filter(game=gdbo, user__in=udbol) # pylint: disable=no-member
        if (not dbdata):
            raise RuntimeError("ERROR: Persistent Data not Found or Mismatched.")
        return dbdata

    @staticmethod
    def get_scsr_list_by_genre(gdbo):
        if not isinstance(gdbo,GameDB):
            raise TypeError("ERROR: Invalid type for the game  data.")
        the_games=GamesGenresDB.seek_genre(gdbo)
        the_data=ScsrDB.objects.filter(game__in=the_games.gamesList) # pylint: disable=no-member
        return the_data

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ Prior to saving the scsr, guarantees its consistencies
        
        Arguments:
            sender {scsrDB} -- The sender of the signal
            document {scsrDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

    


signals.pre_save.connect(ScsrDB.pre_save, sender=ScsrDB)


class ConsolidatedScsrDB(db.Document):
    game = db.ReferenceField(GameDB, db_field="db_game", required=True, primary_key=True)  # pylint: disable=no-member
    assessments = db.IntField(db_field="assessments", required=True, default=1) # pylint: disable=no-member
    date_creation = db.DateTimeField(db_field="date_creation", required=True, default=datetime.utcnow) # pylint: disable=no-member
    date_modified = db.DateTimeField(db_field="date_modified", required=True, default=datetime.utcnow) # pylint: disable=no-member
    """History will store the dict with the quantified data in the following form: [{
        "persuasive":{"interactivity":{element_id:qtt}...}
        }]
    """

    history = db.ListField(db_field="history", required = True, default=[]) # pylint: disable=no-member

    @staticmethod
    def get_consolidated(game):
        if not isinstance(game,GameAO):
            raise TypeError("ERROR: Argument is not a valid GameAO")
        do_have=ConsolidatedScsrDB.objects.filter(game=game.__get_persisted__()).first() # pylint: disable=no-member
        if do_have:
            """
                If the data is less than a week (computed in a weekly basis) and there are data in the history
            """
            week=timedelta(days=7)
            agora=datetime.utcnow()
            if(agora-do_have.date_modified<week):
                return do_have.to_json()
            """
                Else, create new computation for an existing do_have and assign the history.
                do_have.date_modified=datetime.utcnow()
            """
        else:
            #there is no do_have, a new one is needed
            do_have=ConsolidatedScsrDB()
            do_have.game=game.__get_persisted__()
            do_have.date_creation=datetime.utcnow()
        game_scsr_list=ScsrDB.get_scsr_list_by_game(game.__get_persisted__())
        the_sum=sum(game_scsr_list)
        the_quant=the_sum.quantify()
        do_have.history.append(the_quant)
        do_have.date_modified=datetime.utcnow()
        do_have.assessments=ScsrDB.objects.filter(game=game.__get_persisted__()).count() # pylint: disable=no-member
        do_have.save()
        return do_have

    def to_json(self):
        current=self.history[-1]
        #the json to be returned is based on a ScsrAO object, only including the quantification data for each element
        return {
            "persuasive":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['interactivity']),
                "ludic":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['ludic']),
                "gamefication":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['gamefication'])
            },
            "aesthetic":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['aesthetic']['interactivity']),
                "ludic":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['aesthetic']['ludic'])
            },
            "orchestration":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['interactivity']),
                "mechanical":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['mechanical']),
                "gamefication":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['gamefication']),
            },
            "reification":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['interactivity']),
                "mechanical":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['mechanical']),
                "device":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['device'])
            }
        }

    def history_json(self):
        #the json to be returned is based on a ScsrAO object, only including the quantification data for each element
        return [{
            "persuasive":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['interactivity']),
                "ludic":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['ludic']),
                "gamefication":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['persuasive']['gamefication'])
            },
            "aesthetic":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['aesthetic']['interactivity']),
                "ludic":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['aesthetic']['ludic'])
            },
            "orchestration":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['interactivity']),
                "mechanical":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['mechanical']),
                "gamefication":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['orchestration']['gamefication']),
            },
            "reification":{
                "interactivity":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['interactivity']),
                "mechanical":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['mechanical']),
                "device":({"element":dado["element"].to_obj().to_json(),"count":dado["count"]} for dado in current['reification']['device'])
            }
        } for current in self.history]

    @classmethod
    def preSave(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())
        pass

signals.pre_save.connect(ConsolidatedScsrDB.preSave, sender=ConsolidatedScsrDB)



