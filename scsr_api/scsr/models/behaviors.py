from mongoengine import signals
from uuid import uuid4
import copy
from collections import abc
from datetime import datetime
from application import db
from scsr.models.elements import ElementDB, ElementAO

class BehaviorDiffDB(db.Document):
    elements_added = db.ListField(db.ReferenceField(ElementDB), db_field="elements_added", default=[]) # pylint: disable=no-member
    elements_removed = db.ListField(db.ReferenceField(ElementDB), db_field="elements_removed",default=[]) # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", required=True, default=datetime.utcnow) # pylint: disable=no-member

    """ Returns the diff object for this data.
        Since the diff is only manipulated in the Application Level, all the data returned are AO
    
    """

    def to_obj(self):
        return {
            "created":self.created,
            "diff": {
                "added":set(elt.to_obj() for elt in self.elements_added),
                "removed":set(elt.to_obj() for elt in self.elements_removed)
            }
        }

    def to_json(self):
        return {
            "created":self.created,
            "diff": {
                "added":set(elt.to_json() for elt in self.elements_added),
                "removed":set(elt.to_json() for elt in self.elements_removed)
            }
        }

    def __repr__(self):
        return f"Added: {self.elements_added} ||| Removed: {self.elements_removed}"

class BehaviorAO(abc.MutableSet):
    
    def __init__(self, elements=(), behavior_type=""):
        if(behavior_type):
            if(behavior_type not in ["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE", "composed"]):
                raise TypeError("ERROR: Behavior type not recognized. Type provided: "+behavior_type)

        self.elements = set(elements)

        self.behavior_type = behavior_type

        self.external_id=""
        # element_count will provide the quantification for the j_son. It does not take part in the representation.
        # quantification operations (+) sets the behavior type so it does not allows saving
        # logic (and set) operations maintains only one instance, preserving the set properties.
        #   -- HOWEVER! Comparison between different types of behaviors are allowed, but does not allow saving.
        self.element_count = list(elements)
        self.updated=datetime.utcnow()
        self.diffdata=[]


    @staticmethod
    def from_db(db_obj):
        if(not isinstance(db_obj,BehaviorDB)):
            raise TypeError("ERROR: Argument is not a valid BehaviorDB object")
        retorno=BehaviorAO([element.to_obj() for element in db_obj.elements],db_obj.behavior_type)
        retorno.external_id=db_obj.external_id
        retorno.updated=db_obj.updated
        retorno.diffdata=[difd.to_obj() for difd in db_obj.diffdata]
        return retorno


    def __semi_hash__(self):
        """
            The __semi_hash__ constructs the string representing the behavior disregarding if it is DB or AO
            This allows for semi-contextual, but meaningful, comparisons and code economy.
            The calculation is performed in the following form:
                the external_id concatenated with
                the behavior type
                the string concatenation of every element semi_hashes (as string), provided in a sorted list
                the element_count does not participates in the process
        """
        the_ret=""+str(self.external_id)+" - "+self.behavior_type+" - "
        el_list=[el.__semi_hash__() for el in self.elements]
        el_list.sort()
        for element in el_list:
            the_ret+=f"{element} - "
        return the_ret

    def __hash__(self):
        the_string="AO "+self.__semi_hash__()
        return hash(the_string)

    def revert_diff(self,difdata):
        """ Reverts current structure with diff data. (maintaining the diff_data structure)
        
        Arguments:
            difdata {dict} -- The dictionary of diff data. The diffdata is composed of the element as key and 1, if added or -1, if removed.
        
        Returns:
            BehaviorAO -- the same object, with the elements altered.
        """
        #check diff structure:
        if not isinstance(difdata,dict):
            return self.elements
        data=self.elements.copy()
        self.elements=(data-difdata["diff"]["added"])|difdata["diff"]["removed"]
        return self

    def reset(self):
        #only maintains diffdata
        self.elements=set()
        self.element_count=[]
        self.save()
        return self

    def __contains__(self, element):
        return element in self.elements

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)

    def __or__(self, other):
        the_type=self.behavior_type
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.behavior_type==other.behavior_type:
            the_type="composed" #composed type cannot be saved!
        retorno=self.__class__(self.elements | other.elements, behavior_type=the_type)
        return retorno

    def __and__(self, other):
        the_type=self.behavior_type
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.behavior_type==other.behavior_type:
            the_type="composed" #composed type cannot be saved!
        retorno = self.__class__(self.elements & other.elements, behavior_type=the_type)
        return retorno

    def __xor__(self, other):
        the_type=self.behavior_type
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.behavior_type==other.behavior_type:
            the_type="composed" #composed type cannot be saved!
        retorno = self.__class__(self.elements ^ other.elements, behavior_type=the_type)
        return retorno

    def __sub__(self,other):
        the_type=self.behavior_type
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        if not self.behavior_type==other.behavior_type:
            the_type="composed" #composed type cannot be saved!
        retorno = self.__class__(self.elements - other.elements, behavior_type=the_type)
        return retorno

    #__radd__ can add BehaviorAO+0, that's why we check the validity. If valid it must be a BehaviorAI
    # if not valid, then create an empty BehaviorAO and perform the add
    def __radd__(self,other):
        the_type=self.behavior_type
        if other:
            if not isinstance(other,BehaviorAO):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
            if not self.behavior_type==other.behavior_type:
                the_type="composed"
        else:
            other=BehaviorAO()
        retorno=self|other
        retorno.element_count=self.element_count+other.element_count
        retorno.type=the_type
        return retorno

    # Unlike __radd__, where the other can be 0 (used for sum), __add__ demands an argument.
    def __add__(self,other):
        the_type=self.behavior_type
        if not isinstance(other,BehaviorAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        if not self.behavior_type==other.behavior_type:
            the_type="composed"
        retorno=self|other
        retorno.element_count=self.element_count+other.element_count
        retorno.type=the_type
        return retorno

    def diff(self,other):
        if not isinstance(other,BehaviorAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        present=self.elements.difference(other.elements)
        absent=other.elements.difference(self.elements)
        return {
            "created":datetime.utcnow,
            "added":present,
            "removed":absent,
            "derivation":self.behavior_type + " - " + other.behavior_type
        }


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

        present=[]
        absent=[]
        if not isinstance(one, BehaviorAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        for other in others:
            if not isinstance(other,BehaviorAO):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
            present=present+list(one.elements.difference(other.elements))
            absent=absent+list(other.elements.difference(one.elements))
        return {
            "created":datetime.utcnow,
            "added":present,
            "removed":absent,
            "derivation":one.behavior_type + " - " + other.behavior_type
        }
        

    @staticmethod
    def s_diff(one,other):
        if not isinstance(other,BehaviorAO) or not isinstance(one,BehaviorAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        present=one.elements.difference(other.elements)
        absent=other.elements.difference(one.elements)
        return {
            "created": datetime.utcnow,
            "added": present,
            "removed": absent,
            "derivation": one.behavior_type + " - " + other.behavior_type
        }

    def add(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        if not self.__contains__(element):
            self.elements.add(element)
            self.element_count.append(element)

    def discard(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        #it uses only ther external_id for the element data.
        self.elements.discard(element)
        #discard removes all occurrences of the element
        while element in self.element_count:
            self.element_count.remove(element)

    def quantify(self): 
        """ Returns the dictionary of the quantification of the elements.
        
        Returns:
            set containing a dict with the element DB object as 'element' and how many times it occurs as 'count'
        """

        return ({"element":element.__get_persisted__(),"count":self.element_count.count(element)} for element in self.elements)

    def to_json(self):
        return {
            "behavior_type": self.behavior_type,
            "elements": [el.to_json() for el in self.elements]
        }

    def __repr__(self):
        base = f"{self.behavior_type}: {self.elements}"
        return base

    @staticmethod
    def get_behavior(external_id_):
        if not isinstance(external_id_,str):
            raise TypeError("ERROR: Parameter is not a string! Definitively not a valid key.")
        db_obj=BehaviorDB.objects.filter(external_id=external_id_).first() # pylint: disable=no-member
        if not db_obj:
            raise RuntimeError("Error: No persistence data found for id: "+external_id_)
        return db_obj.to_obj()

    @staticmethod
    def create_behavior(behtype):
        
        the_beh=BehaviorDB.__create_persistence__(behtype)
        return the_beh.to_obj()


    def check_save(self):
        print("Check saving. Element ID = "+self.external_id)
        # To save, the behavior must exist.
        if len(self.external_id)<1:
            return RuntimeError,"ERROR: Attempting to save a BehaviorAO without a valid id."
        # To save, the behavior must be consistent!
        if self.behavior_type not in ["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE"]:
            return TypeError,"Behavior Type not Recognized."
        # And all elements in the list must be valid ElementAO objects
        for element in self.elements:
            if not isinstance(element,ElementAO):
                return TypeError,"Attempting to save a non ElementAO object"
        #Behavior mus ALWAYS have an external ID. 
        # Its creation responsibility is of the function/role which it composes.
        return None,""

    def save(self):
        """ Persists the behavior data.
        
        Raises:
            TypeError -- Behavior must have the type defined and of specific value
            TypeError -- All objects in the set must be of ElementAO type and persisted. I.e.: Have a valid external_id
        """
        errorType,msg = self.check_save()
        if errorType:
            raise errorType(msg)
        #Persists and update self data.
        returned_obj=BehaviorDB.__persist__(self)
        self.updated=returned_obj.updated
        self.diffdata=[difd.to_obj() for difd in returned_obj.diffdata]
        return self
    
    def copy(self):
        to_ret=BehaviorAO(self.elements.copy(), self.behavior_type)
        return to_ret

    def difference(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        retorno=self ^ other
        retorno=retorno & self
        return retorno

    def difference_update(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        if other.behavior_type != self.behavior_type:
            raise TypeError("ERROR: Cannot DiffUpdate different types of behaviors.")
        retorno=self ^ other
        retorno=retorno & self
        self.element_count=retorno.element_count
        self.elements = retorno.elements
        self.behavior_type = retorno.behavior_type

    def intersection(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        return self & other
    
    def union(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        return self | other

    def union_update(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        if other.behavior_type != self.behavior_type:
            raise TypeError("ERROR: Cannot DiffUpdate different types of behaviors.")
        retorno= self | other
        self.element_count=retorno.element_count
        self.elements = retorno.elements
        self.behavior_type = retorno.behavior_type
        

    def intersection_update(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        if other.behavior_type != self.behavior_type:
            raise TypeError("ERROR: Cannot DiffUpdate different types of behaviors.")
        retorno= self & other
        self.element_count=retorno.element_count
        self.elements = retorno.elements
        self.behavior_type = retorno.behavior_type

    def symmetric_difference(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        retorno=self ^ other
        return retorno

    def symmetric_difference_update(self,other):
        if not isinstance(other, BehaviorAO):
            raise TypeError("ERROR: Trying to operate two different, non related objects")
        if other.behavior_type != self.behavior_type:
            raise TypeError("ERROR: Cannot DiffUpdate different types of behaviors.")
        retorno=self ^ other
        self.element_count=retorno.element_count
        self.elements = retorno.elements
        self.behavior_type = retorno.behavior_type

    for method in ['clear', 'isdisjoint', 'issubset', 'issuperset', 'pop', 'remove', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.elements, method)(*((other,) if other else ()) ) ) (method)


class BehaviorDB(db.Document):
    """ ORM for the behavior collections to be assigned to the function
        The collection is formed of the elements provided by the users.
        The collection represents a set contextualized within the intrinsic behavior of the element.
        The basic behaviors are:
            - Interactivity: Elements that provides or demands interaction by the user. Move, Grab, Drop, Push, Button, Lever, Controller, Guitar, ...
            - Ludic: Elements within the context of philosophy, pedagogy or psychology, not properly assessed in the research in the field of engineering.
            - Mechanical: Elements that communicates within the system. Provides responses to the system or rules. Ex: Kill (demands an Interactivity 'Shoot' and a Mechanical 'hit' or 'collide') or even Player Character (or Avatar), it communicates with the system)
            - Gamfication: Anything that stores a value or a state. HighScore, for instance.
            - Device: Anything physical: Controller, Computer, Cartridge, Meeple, Dice, Miniature...
    """

    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    elements = db.ListField(db.ReferenceField(ElementDB), db_field="elements", default=[]) # pylint: disable=no-member
    behavior_type = db.StringField(db_field="behavior", required=True, choices=["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE"], default="LUDIC") # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", required=True, default=datetime.utcnow) # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", required=True, default=datetime.utcnow) # pylint: disable=no-member
    #diffdata is a list of differentials, passible of sorting via creation date
    diffdata = db.ListField(db.ReferenceField(BehaviorDiffDB),db_field="diffdata") # pylint: disable=no-member

    def __repr__(self):
        base = f"{self.behavior_type}: {self.elements} - {len(self.diffdata)-1} updates"
        return base


    def __semi_hash__(self):
        """
            The __semi_hash__ constructs the string representing the behavior disregarding if it is DB or AO
            This allows for faster comparisons and code economy.
            The calculation is performed in the following form:
                the external_id concatenated with
                the behavior type
                the string concatenation of every element semi_hashes (as string), provided in a sorted list
        """
        the_ret=""+str(self.external_id)+" - "+self.behavior_type+" - "
        el_list=[el.__semi_hash__() for el in self.elements]
        el_list.sort()
        for element in el_list:
            the_ret+=f"{element} - "
        return the_ret

    def __hash__(self):
        the_string="DB "+self.__semi_hash__()
        return hash(the_string)

        

    def to_obj(self):
        return BehaviorAO.from_db(self)

    @staticmethod
    def __persist__(behob):
        if not isinstance(behob,BehaviorAO):
            raise TypeError("ERROR: Cannot persist a non Behavior type in the Behavior Collection!")
        if behob.behavior_type not in ["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE"]:
            raise TypeError("Behavior Type not Recognized.")
        db_obj=None
        if not behob.external_id:
            raise RuntimeError("ERROR: Cannot persist a nonexistent data!")
        db_obj=BehaviorDB.objects.filter(external_id=behob.external_id).first() # pylint: disable=no-member
        if not db_obj:
            raise RuntimeError("ERROR: Persisted Behavior Data not Found!")
        #copy the returned (previous) data
        previous=db_obj.elements.copy()
        #updates the object list
        the_ids=[elt.external_id for elt in behob.elements]
        db_obj.elements=ElementDB.objects.filter(external_id__in = the_ids) # pylint: disable=no-member
        #guarantees the same behavior type
        db_obj.behavior_type=behob.behavior_type
        #generates the Diff structure
        added=list(set(db_obj.elements).difference(set(previous)))
        removed=list(set(previous).difference(set(db_obj.elements)))
        the_diff=BehaviorDiffDB()
        the_diff.elements_added=added
        the_diff.elements_removed=removed
        the_diff.save()
        db_obj.diffdata.append(the_diff)
        db_obj.updated=datetime.utcnow()
        db_obj.save()
        return db_obj.to_obj()

    @staticmethod
    def __create_persistence__(behavior_type):
        if not behavior_type:
            raise RuntimeError("Behavior Type must be specified and be within the specified values.")
        if behavior_type not in ["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE"]:
            raise TypeError("Behavior Type not Recognized.")
        the_pers=BehaviorDB()
        the_pers.behavior_type=behavior_type
        firstDiff=BehaviorDiffDB()
        firstDiff.save()
        the_pers.diffdata.append(firstDiff)
        the_pers.save()
        return the_pers

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ Previous to saving the behavior set the external_id
        
        Arguments:
            sender {BehaviorDB} -- The sender of the signal
            document {BehaviorDB} -- The instance of the document
        """
        # check the previous state
        if not document.external_id:
            #create an external_id if none exists
            document.external_id=str(uuid4())
            #set the previous document to an empty behavior list
        if not document.behavior_type in ["INTERACTIVITY", "LUDIC", "MECHANICAL", "GAMEFICATION", "DEVICE"]:
            raise RuntimeError("ERROR: Attempting to save an invalid behavior type: "+document.behavior_type)


signals.pre_save.connect(BehaviorDB.pre_save, sender=BehaviorDB)


