from mongoengine import signals
from uuid import uuid4
from application import db
from collections import abc
from datetime import datetime
from scsr.models.behaviors import BehaviorDB, BehaviorAO
from scsr.models.elements import ElementAO, ElementDB
from application import the_log

"""The functions aggregates behaviors. They were created to provide easy coding and code reading, as well as the behaviors.
    Each function is formed by the following fields:
        external_id - unique identification code to represent this function representation
        specific behavior set - each function have their specific set of behaviors.
"""

    

class AestheticFunctionDB(db.Document):
    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    interactivity = db.ReferenceField(BehaviorDB, db_field="interactivity", required=True) # pylint: disable=no-member
    ludic = db.ReferenceField(BehaviorDB, db_field="ludic", required=True) # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", required=True, default=datetime.utcnow) # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", required=True, default=datetime.utcnow) # pylint: disable=no-member
    def to_obj(self):
        return AestheticFunctionAO.from_db(self)

    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno+="\n"+"*"*50+"\ninteractivity: "+self.interactivity.__repr__()
        retorno+="\n"+"*"*50+"\nludic: "+self.ludic.__repr__()
        return retorno


    def __semi_hash__(self):
        """
            The __semi_hash__ constructs the string representing the function disregarding if it is DB or AO
            This allows for semi-contextual, but meaningful, comparisons and code economy.
            The calculation is performed in the following form:
                the external_id concatenated with
                the string concatenation of every behavior semi_hashes (as string), provided in a sorted list
            Returns the string computed.
        """
        the_ret=(self.external_id if self.external_id else "None")+" - "+self.interactivity.__semi_hash__()+" - "+self.ludic.__semi_hash__()

        return the_ret

    def __hash__(self):
        the_string="DB "+self.__semi_hash__()
        return hash(the_string)

    @staticmethod
    def __persist__(pf):
        if not isinstance(pf,AestheticFunctionAO):
            raise TypeError("ERROR: Argument is not a valid AestheticFunctionAO object.")
        #get the DB object of the function
        to_save=AestheticFunctionDB.objects.filter(external_id=pf.external_id).first() # pylint: disable=no-member
        if not to_save:
            raise RuntimeError("ERROR: Unable to retrieve reference to persist - AestheticFunctionDB - "+pf.external_id)
        #Behavior objects already saved. Just retrieve the DB reference from them
        interDB=BehaviorDB.objects.filter(external_id=pf.interactivity.external_id).first() # pylint: disable=no-member
        ludDB=BehaviorDB.objects.filter(external_id=pf.ludic.external_id).first() # pylint: disable=no-member
        to_save.interactivity=interDB
        to_save.ludic=ludDB
        to_save.updated=datetime.utcnow()
        try:
            to_save.save()
        except:
            the_log.log("ERROR: Aesthetic Function not persisted in _persist_.")
        finally:
            return to_save

        
        

    @staticmethod
    def __create_persistence__():
        """ Create the persistence object for the aesthetic function. (use as constructor)
            The behaviors are created and assigned to the function
            If errors occur, the behaviors will be deleted and the function will not be created
        
            Raises:
                RuntimeError -- Error creating the behaviors
                RuntimeError -- Error creating AestheticFunctionDB - external_id not returned
                RuntimeError -- Error creating AestheticFunctionDB - general error
            
            Returns:
                AestheticFunctionDB -- The DB object persisted (with valid external_id and oid)
            """

        to_save=AestheticFunctionDB()
        ludic_=None
        interactivity_=None
        not_err=set()
        # Try creating the behaviors. Adding to the not_err set
        try:
            ludic_=BehaviorDB.__create_persistence__("LUDIC")
            interactivity_=BehaviorDB.__create_persistence__("INTERACTIVITY")
            #set the data for the bookkeping if error happened
            not_err=set([ludic_,interactivity_])

            if not ludic_ or not ludic_.external_id:
                #error persisting ludic. discard it from the set
                not_err.discard(ludic_)
            if not interactivity_ or not interactivity_.external_id:
                #error persisting interactivity. discard it from the set
                not_err.discard(interactivity_)
        except RuntimeError as e:
            for beh in not_err:
                #it was created, so we delete... it is empty!
                beh.delete()
            raise RuntimeError("ERROR: Error creating BehaviorDB Object. "+str(e))
        #all were created, no error made
        to_save.ludic=ludic_
        to_save.interactivity=interactivity_
        try:
            to_save.save()
            if not to_save.external_id:
                #there goes all the work! if no external_id is provided, it is an error!
                ludic_.delete()
                interactivity_.delete()
                raise RuntimeError("ERROR: Error creating AestheticFunctionDB object. Persistence did not return an external_id")
        except RuntimeError as e:
            #there goes all the work!
            ludic_.delete()
            interactivity_.delete()
            raise RuntimeError("ERROR: Error creating AestheticFunctionDB object. - "+str(to_save),e)
        return to_save

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ prior to saving the function it is needed to guarantee saving their reference data. (is it?)
        
        Arguments:
            sender {AestheticFunctionDB} -- The sender of the signal
            document {AestheticFunctionDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

signals.pre_save.connect(AestheticFunctionDB.pre_save, sender=AestheticFunctionDB)

#As with Behaviors, FunctionAO objects must not be created for manipulation. A FunctionAO may always have an ExternalID.
class AestheticFunctionAO(abc.MutableSet):
    
    def __init__(self, interactivity_=None, ludic_=None):
        """Constructor, only valid with valid BehaviorAO's
        
        Keyword Arguments:
            interactivity_ {BehaviorAO} -- BehaviorAO object referring to interactivity (default: {None})
            ludic_ {BehaviorAO} -- BehaviorAO object referring to ludic (default: {None})
        
        Raises:
            TypeError -- Argument is not a valid BehaviorAO object
            TypeError -- Argument is not a valid BehaviorAO object
            TypeError -- Argument is not a valid BehaviorAO object
        """

        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR: Argument/Parameter is not a valid BehaviorAO - Interactivity.")
        if not isinstance(ludic_,BehaviorAO):
            raise TypeError("ERROR: Argument/Parameter is not a valid BehaviorAO - Ludic.")
        self.interactivity = interactivity_
        self.ludic = ludic_
        self.external_id = None
        self.updated=""
        self.created=""

        #set indicates what elements are in the function (the union of all behaviors)
        self.elements = set((self.interactivity | self.ludic).elements)
        #unassigned elements indicates what elements must be assigned.
        #The function can only be persisted if this list is empty.
        self.unassigned_element=list()
        self.composed=False


    def quantify(self):
        return {
            "interactivity": self.interactivity.quantify(),
            "ludic": self.ludic.quantify()
        }


    @staticmethod
    def from_db(db_obj):
        if(not isinstance(db_obj,AestheticFunctionDB)):
            raise TypeError("Parameter is not a valid AestheticFunctionDB object.")
        retorno = AestheticFunctionAO(db_obj.interactivity.to_obj(),db_obj.ludic.to_obj())
        retorno.external_id = db_obj.external_id
        retorno.updated=db_obj.updated
        retorno.created = db_obj.created
        return retorno

    @staticmethod
    def create_function():
        the_db=AestheticFunctionDB.__create_persistence__()
        return the_db.to_obj()

    def to_json(self):
        retorno={
            "external_id":self.external_id,
            "interactivity":self.interactivity.to_json(),
            "ludic":self.ludic.to_json()
        }
        return retorno
    
    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno+="\n"+"*"*50+"\ninteractivity: "+self.interactivity.__repr__()
        retorno+="\n"+"*"*50+"\nludic: "+self.ludic.__repr__()
        return retorno

    def __semi_hash__(self):
        """
            The __semi_hash__ constructs the string representing the function disregarding if it is DB or AO
            This allows for semi-contextual, but meaningful, comparisons and code economy.
            The calculation is performed in the following form:
                the external_id (if not present, it must be a composed) concatenated with
                the string concatenation of every behavior semi_hashes (as string), provided in a sorted list
            Returns the string computed.
        """
        the_ret=(self.external_id if self.external_id else "None")+" - "+self.interactivity.__semi_hash__()+" - "+self.ludic.__semi_hash__()

        return the_ret

    def __hash__(self):
        the_string="AO "+self.__semi_hash__()
        return hash(the_string)

    """ 
        Decide how to deal with:
            Add:
                Adds an element to the set, if not already, and to the unassigned list (always)
            Discard
                Discards the element from the unassigned list, the element set and from each behavior. Literally discard the element from the function
            __contains__
                Check if the element is in the role.
            __iter__
                Iters the element in the set
            __len__
                The length of the elements in this role (length of the set)
    """
    
    def add(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        if not self.__contains__(element):
            self.elements.add(element)
        self.unassigned_element.append(element)

    def discard(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("element is not a valid ElementAO object")
        #it uses only ther external_id for the element data.
        self.elements.discard(element)
        #discard removes all occurrences of the element
        while element in self.unassigned_element:
            self.unassigned_element.remove(element)
        self.interactivity.discard(element)
        self.ludic.discard(element)


    def __contains__(self, element):
        return element in self.elements

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)


    def reset(self):
        # Reset all behaviors
        self.elements=set()
        self.unassigned_element=[]
        self.interactivity.reset()
        self.ludic.reset()
        self.save()
        return self

    # The operations discards the unassigned items
    def __or__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity | other.interactivity, self.ludic | other.ludic)
        return retorno

    def __and__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity & other.interactivity, self.ludic & other.ludic)
        return retorno

    def __xor__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity ^ other.interactivity, self.ludic ^ other.ludic)
        return retorno

    def __sub__(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity - other.interactivity, self.ludic - other.ludic)
        return retorno

    #__radd__ can add BehaviorAO+0, that's why we check the validity. If valid it must be a BehaviorAI
    # if not valid, then create an empty BehaviorAO and perform the add
    def __radd__(self,other):
        if other:
            if not isinstance(other,self.__class__):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
        else:
            #The identity element
            other=AestheticFunctionAO()
        retorno = AestheticFunctionAO(self.interactivity+other.interactivity, self.ludic+other.ludic)
        #Indicates a composed, quantified element. In order to save it must be 1: Normalized, 2: Applied to a valid gamegesis.
        self.composed=True
        return retorno

    # Unlike __radd__, where the other can be 0 (used for sum), __add__ demands an argument.
    def __add__(self,other):
        if not isinstance(self.__class__):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        retorno = AestheticFunctionAO(self.interactivity+other.interactivity, self.ludic+other.ludic)
        #Indicates a composed, quantified element. In order to save it must be 1: Normalized, 2: Applied to a valid gamegesis.
        self.composed=True
        return retorno

    def diff(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Trying to create a diff between different roles!")
        retorno={
            "interactivity":self.interactivity.diff(other.interactivity),
            "ludic":self.ludic.diff(other.ludic)
        }
        return retorno

    @staticmethod
    def s_diff(one,other):
        if not isinstance(other,AestheticFunctionAO) or not isinstance(one,AestheticFunctionAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        retorno={
            "interactivity":one.interactivity.diff(other.interactivity),
            "ludic":one.ludic.diff(other.ludic),
        }
        return retorno

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
        self.interactivity.revert_diff(difdata['interactivity'])
        self.ludic.revert_diff(difdata['ludic'])
        return self


    @staticmethod
    def get_function(external_id_):
        if not isinstance(external_id_,str):
            raise TypeError("ERROR: Parameter is not a string! Definitively not a valid key.")
        db_obj=AestheticFunctionDB.objects.filter(external_id=external_id_).first() # pylint: disable=no-member
        if not db_obj:
            raise RuntimeError("Error: No persistence data found for aesthetic function id: "+external_id_)
        return db_obj.to_obj()

    def save(self):
        """ Persists the aesthetic function data.
            This persistence is given the following form:
            1 - The function must not have unassigned elements
            2 - Each behavior is saved. If one incurs error, the others are not saved. the function is not saved.
                2.1 - If behaviors are saved, and error occurs afterwards, ok. The behavior data persistence is valid, but the function is not.
            3 - The function is saved.
        
        Raises:
            TypeError -- Behavior must have the type defined and of specific value
            TypeError -- All objects in the set must be of ElementAO type and persisted. I.e.: Have a valid external_id
        """
        if len(self.unassigned_element)>0:
            raise RuntimeError("ERROR: Function must not have unassigned elements!")
        lud=self.ludic
        inter=self.interactivity
        try:
            #save the behaviors
            self.interactivity=self.interactivity.save()
            self.ludic=self.ludic.save()
        except:
            if self.ludic!=lud:
                self.ludic=lud
            if self.interactivity!=inter:
                self.interactivity=inter
            raise RuntimeError("ERROR: Some of the aesthetic function behaviors were not saved. ")
        #try saving the function
        try:
            AestheticFunctionDB.__persist__(self)
        except:
            raise RuntimeError("ERROR: Not able to save the Aesthetic Function: "+self.external_id)

    ############################# Setters and Removals (without perssistence)

    def add_ludic_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.ludic.add(element)
        self.elements.add(element)

    def discard_ludic_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.ludic:
            self.ludic.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity))):
                self.elements.discard(element)

    def add_interactivity_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.interactivity.add(element)
        self.elements.add(element)

    def discard_interactivity_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.interactivity:
            self.interactivity.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.ludic))):
                self.elements.discard(element)


    def set_interactivity(self,interactivity_):
        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if interactivity_.behavior_type!="INTERACTIVITY":
            raise TypeError("ERROR! Assigning a Non INTERACTIVITY Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.interactivity.elements=interactivity_.elements


    def set_ludic(self,ludic_):
        if not isinstance(ludic_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if ludic_.behavior_type!="LUDIC":
            raise TypeError("ERROR! Assigning a Non ludic Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.ludic.elements=ludic_.elements

    def reset_ludic(self):
        self.ludic.reset()
        
    def reset_interactivity(self):
        self.interactivity.reset()

    #########################################################################

    ############################# Setters and Removals (with perssistence)

    def p_add_ludic_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.ludic.add(element)
        self.elements.add(element)
        self.ludic.save()

    def p_discard_ludic_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.ludic:
            self.ludic.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity))):
                self.elements.discard(element)
        self.ludic.save()

    def p_add_interactivity_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.interactivity.add(element)
        self.elements.add(element)
        self.interactivity.save()

    def p_discard_interactivity_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.interactivity:
            self.interactivity.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.ludic))):
                self.elements.discard(element)
        self.interactivity.save()

    def p_set_interactivity(self,interactivity_):
        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if interactivity_.behavior_type!="INTERACTIVITY":
            raise TypeError("ERROR! Assigning a Non INTERACTIVITY Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.interactivity.elements=interactivity_.elements
        self.interactivity.save()


    def p_set_ludic(self,ludic_):
        if not isinstance(ludic_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if ludic_.behavior_type!="LUDIC":
            raise TypeError("ERROR! Assigning a Non ludic Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.ludic.elements=ludic_.elements
        self.ludic.save()


    def p_reset_ludic(self):
        self.ludic.reset()
        self.ludic.save()
        
    def p_reset_interactivity(self):
        self.interactivity.reset()
        self.interactivity.save()
        

    #########################################################################

    def copy(self):
        """ 
            Create a copy of the data.
            The behaviors are created anew as well.
            There is no external ID, for none!
                TODO: Check the save method to verify proper assignments to this case!
        """
        to_ret=AestheticFunctionAO(self.interactivity.copy(), self.ludic.copy())
        return to_ret

    def difference(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno = (self ^ other)&self
        return retorno

    def intersection(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno = self & other
        return retorno

    def union(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno = self | other
        return retorno

    def issubset(self,other):
        """ Returns true only if every behavior is a subset of its related behavior in other
        
        Arguments:
            other {AestheticFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_subset=self.interactivity.issubset(other.interactivity)
        lud_subset=self.ludic.issubset(other.ludic)
        return int_subset and lud_subset 

    def issuperset(self,other):
        """ Returns true only if every behavior is a superset of its related behavior in other
        
        Arguments:
            other {AestheticFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_superset=self.interactivity.issuperset(other.interactivity)
        lud_superset=self.ludic.issuperset(other.ludic)
        return int_superset and lud_superset 

    def isdisjoint(self,other):
        """ Return True only if there are no intersections between the related behaviors nor between the elements
        
        Arguments:
            other {AestheticFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_inter=self.interactivity & other.interactivity
        lud_inter=self.ludic & other.ludic
        elem_inter=self.elements & other.elements
        return (not int_inter) and (not lud_inter) and (not elem_inter)

    def isdisjoint_behavior(self,other):
        """ Return True only if there are no intersections only between the related behaviors 
        
        Arguments:
            other {AestheticFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_inter=self.interactivity & other.interactivity
        lud_inter=self.ludic & other.ludic
        return (not int_inter) and (not lud_inter) 

    def symmetric_difference(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        return self ^ other

    def remove(self,element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Operand Type not a valid ElementAO object.")
        if not element in self:
            raise KeyError("ERROR: Element not in function.")
        self.discard(element)

    def pop(self):
        el=self.elements.pop()
        self.elements.add(el)
        beh=[]
        if(el in self.interactivity):
            beh.append("interactivity")
        if(el in self.ludic):
            beh.append("ludic")
        self.discard(el)
        return {
            "element": el,
            "behavior": beh
        }

    for method in ['clear', 'difference_update', 'intersection_update', 'symmetric_difference_update', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.elements, method)(*((other,) if other else ()) ) ) (method)
