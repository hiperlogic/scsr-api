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

    

class ReificationFunctionDB(db.Document):
    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    interactivity = db.ReferenceField(BehaviorDB, db_field="interactivity", required=True) # pylint: disable=no-member
    mechanical = db.ReferenceField(BehaviorDB, db_field="mechanical", required=True) # pylint: disable=no-member
    device = db.ReferenceField(BehaviorDB, db_field="device", required=True) # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", required=True, default=datetime.utcnow) # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", required=True, default=datetime.utcnow) # pylint: disable=no-member

    def to_obj(self):
        return ReificationFunctionAO.from_db(self)

    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno+="\n"+"*"*50+"\ninteractivity: "+self.interactivity.__repr__()
        retorno+="\n"+"*"*50+"\nmechanical: "+self.mechanical.__repr__()
        retorno+="\n"+"*"*50+"\ndevice: "+self.device.__repr__()
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
        the_ret=(self.external_id if self.external_id else "None")+" - "+self.interactivity.__semi_hash__()+" - "+self.mechanical.__semi_hash__()+" - "+" - "+self.device.__semi_hash__()+" - "+str(self.updated)

        return the_ret

    def __hash__(self):
        the_string="DB "+self.__semi_hash__()
        return hash(the_string)

    @staticmethod
    def __persist__(pf):
        if not isinstance(pf,ReificationFunctionAO):
            raise TypeError("ERROR: Argument is not a valid ReificationFunctionAO object.")
        #get the DB object of the function
        to_save=ReificationFunctionDB.objects.filter(external_id=pf.external_id).first() # pylint: disable=no-member
        if not to_save:
            raise RuntimeError("ERROR: Unable to retrieve reference to persist - ReificationFunctionDB - "+pf.external_id)
        #Behavior objects already saved. Just retrieve the DB reference from them
        interDB=BehaviorDB.objects.filter(external_id=pf.interactivity.external_id).first() # pylint: disable=no-member
        ludDB=BehaviorDB.objects.filter(external_id=pf.mechanical.external_id).first() # pylint: disable=no-member
        gameDB=BehaviorDB.objects.filter(external_id=pf.device.external_id).first() # pylint: disable=no-member
        to_save.interactivity=interDB
        to_save.mechanical=ludDB
        to_save.device=gameDB
        to_save.updated=datetime.utcnow()
        try:
            to_save.save()
        except:
            the_log.log("ERROR: Reification Function not persisted in _persist_.")
        finally:
            return to_save

        
        

    @staticmethod
    def __create_persistence__():
        """ Create the persistence object for the reification function. (use as constructor)
            The behaviors are created and assigned to the function
            If errors occur, the behaviors will be deleted and the function will not be created
        
            Raises:
                RuntimeError -- Error creating the behaviors
                RuntimeError -- Error creating ReificationFunctionDB - external_id not returned
                RuntimeError -- Error creating ReificationFunctionDB - general error
            
            Returns:
                ReificationFunctionDB -- The DB object persisted (with valid external_id and oid)
            """

        to_save=ReificationFunctionDB()
        mechanical_=None
        interactivity_=None
        device_=None
        not_err=set()
        # Try creating the behaviors. Adding to the not_err set
        try:
            mechanical_=BehaviorDB.__create_persistence__("MECHANICAL")
            interactivity_=BehaviorDB.__create_persistence__("INTERACTIVITY")
            device_=BehaviorDB.__create_persistence__("DEVICE")
            #set the data for the bookkeping if error happened
            not_err=set([mechanical_,interactivity_,device_])

            if not mechanical_ or not mechanical_.external_id:
                #error persisting mechanical. discard it from the set
                not_err.discard(mechanical_)
            if not interactivity_ or not interactivity_.external_id:
                #error persisting interactivity. discard it from the set
                not_err.discard(interactivity_)
            if not device_ or not device_.external_id:
                #error persisting device. discard it from the set
                not_err.discard(device_)
        except RuntimeError as e:
            for beh in not_err:
                #it was created, so we delete... it is empty!
                beh.delete()
            raise RuntimeError("ERROR: Error creating BehaviorDB Object. "+str(e))
        #all were created, no error made
        to_save.mechanical=mechanical_
        to_save.interactivity=interactivity_
        to_save.device=device_
        try:
            to_save.save()
            if not to_save.external_id:
                #there goes all the work! if no external_id is provided, it is an error!
                mechanical_.delete()
                interactivity_.delete()
                device_.delete()
                raise RuntimeError("ERROR: Error creating ReificationFunctionDB object. Persistence did not return an external_id")
        except RuntimeError as e:
            #there goes all the work!
            mechanical_.delete()
            interactivity_.delete()
            device_.delete()
            raise RuntimeError("ERROR: Error creating ReificationFunctionDB object. - "+str(to_save),e)
        return to_save

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ prior to saving the function it is needed to guarantee saving their reference data. (is it?)
        
        Arguments:
            sender {ReificationFunctionDB} -- The sender of the signal
            document {ReificationFunctionDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

signals.pre_save.connect(ReificationFunctionDB.pre_save, sender=ReificationFunctionDB)

#As with Behaviors, FunctionAO objects must not be created for manipulation. A FunctionAO may always have an ExternalID.
class ReificationFunctionAO(abc.MutableSet):
    
    def __init__(self, interactivity_=None, mechanical_=None, device_=None):
        """Constructor, only valid with valid BehaviorAO's
        
        Keyword Arguments:
            interactivity_ {BehaviorAO} -- BehaviorAO object referring to interactivity (default: {None})
            mechanical_ {BehaviorAO} -- BehaviorAO object referring to mechanical (default: {None})
            device_ {BehaviorAO} -- BehaviorAO object referring to device (default: {None})
        
        Raises:
            TypeError -- Argument is not a valid BehaviorAO object
            TypeError -- Argument is not a valid BehaviorAO object
            TypeError -- Argument is not a valid BehaviorAO object
        """

        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR: Argument/Parameter is not a valid BehaviorAO - Interactivity.")
        if not isinstance(mechanical_,BehaviorAO):
            raise TypeError("ERROR: Argument/Parameter is not a valid BehaviorAO - mechanical.")
        if not isinstance(device_,BehaviorAO):
            raise TypeError("ERROR: Argument/Parameter is not a valid BehaviorAO - device.")
        self.interactivity = interactivity_
        self.mechanical = mechanical_
        self.device = device_
        self.external_id = None
        self.updated=""
        self.created=""

        #set indicates what elements are in the function (the union of all behaviors)
        self.elements = set((self.interactivity | self.mechanical | self.device).elements)
        #unassigned elements indicates what elements must be assigned.
        #The function can only be persisted if this list is empty.
        self.unassigned_element=list()
        self.composed=False

    def quantify(self):
        return {
            "interactivity": self.interactivity.quantify(),
            "mechanical": self.mechanical.quantify(),
            "device": self.device.quantify()
        }


    @staticmethod
    def from_db(db_obj):
        if(not isinstance(db_obj,ReificationFunctionDB)):
            raise TypeError("Parameter is not a valid ReificationFunctionDB object.")
        retorno = ReificationFunctionAO(db_obj.interactivity.to_obj(),db_obj.mechanical.to_obj(),db_obj.device.to_obj())
        retorno.external_id = db_obj.external_id
        retorno.updated=db_obj.updated
        retorno.created = db_obj.created
        return retorno

    @staticmethod
    def create_function():
        the_db=ReificationFunctionDB.__create_persistence__()
        return the_db.to_obj()

    def to_json(self):
        retorno={
            "external_id":self.external_id,
            "interactivity":self.interactivity.to_json(),
            "mechanical":self.mechanical.to_json(),
            "device":self.device.to_json()
        }
        return retorno
    
    def __repr__(self):
        retorno="external_id: "+self.external_id if self.external_id else "None**"
        retorno+="\n"+"*"*50+"\ninteractivity: "+self.interactivity.__repr__()
        retorno+="\n"+"*"*50+"\nmechanical: "+self.mechanical.__repr__()
        retorno+="\n"+"*"*50+"\ndevice: "+self.device.__repr__()
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
        the_ret=(self.external_id if self.external_id else "None")+" - "+self.interactivity.__semi_hash__()+" - "+self.mechanical.__semi_hash__()+" - "+" - "+self.device.__semi_hash__()

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
        self.mechanical.discard(element)
        self.device.discard(element)


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
        self.mechanical.reset()
        self.device.reset()
        self.save()
        return self

    # The operations discards the unassigned items
    def __or__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity | other.interactivity, self.mechanical | other.mechanical, self.device | other.device)
        return retorno

    def __and__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity & other.interactivity, self.mechanical & other.mechanical, self.device & other.device)
        return retorno

    def __xor__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity ^ other.interactivity, self.mechanical ^ other.mechanical, self.device ^ other.device)
        return retorno

    def __sub__(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        retorno=self.__class__(self.interactivity - other.interactivity, self.mechanical - other.mechanical, self.device - other.device)
        return retorno

    #__radd__ can add BehaviorAO+0, that's why we check the validity. If valid it must be a BehaviorAI
    # if not valid, then create an empty BehaviorAO and perform the add
    def __radd__(self,other):
        if other:
            if not isinstance(other,self.__class__):
                raise TypeError("ERROR: Trying to sum two different, non related objects")
        else:
            #The identity element
            other=ReificationFunctionAO()
        retorno = ReificationFunctionAO(self.interactivity+other.interactivity, self.mechanical+other.mechanical, self.device+other.device)
        #Indicates a composed, quantified element. In order to save it must be 1: Normalized, 2: Applied to a valid gamegesis.
        self.composed=True
        return retorno

    # Unlike __radd__, where the other can be 0 (used for sum), __add__ demands an argument.
    def __add__(self,other):
        if not isinstance(self.__class__):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        retorno = ReificationFunctionAO(self.interactivity+other.interactivity, self.mechanical+other.mechanical, self.device+other.device)
        #Indicates a composed, quantified element. In order to save it must be 1: Normalized, 2: Applied to a valid gamegesis.
        self.composed=True
        return retorno

    def diff(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Trying to create a diff between different roles!")
        retorno={
            "interactivity":self.interactivity.diff(other.interactivity),
            "mechanical":self.mechanical.diff(other.mechanical),
            "device":self.device.diff(other.device)
        }
        return retorno

    @staticmethod
    def s_diff(one,other):
        if not isinstance(other,ReificationFunctionAO) or not isinstance(one,ReificationFunctionAO):
            raise TypeError("ERROR: Trying to sum two different, non related objects")
        retorno={
            "interactivity":one.interactivity.diff(other.interactivity),
            "mechanical":one.mechanical.diff(other.mechanical),
            "device":one.device.diff(other.device)
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
        self.mechanical.revert_diff(difdata['mechanical'])
        self.device.revert_diff(difdata['device'])
        return self


    @staticmethod
    def get_function(external_id_):
        if not isinstance(external_id_,str):
            raise TypeError("ERROR: Parameter is not a string! Definitively not a valid key.")
        db_obj=ReificationFunctionDB.objects.filter(external_id=external_id_).first() # pylint: disable=no-member
        if not db_obj:
            raise RuntimeError("Error: No persistence data found for reification function id: "+external_id_)
        return db_obj.to_obj()

    def save(self):
        """ Persists the reification function data.
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
        gamef=self.device
        lud=self.mechanical
        inter=self.interactivity
        try:
            #save the behaviors
            self.interactivity=self.interactivity.save()
            self.mechanical=self.mechanical.save()
            self.device=self.device.save()
        except:
            if self.device!=gamef:
                self.device=gamef
            if self.mechanical!=lud:
                self.mechanical=lud
            if self.interactivity!=inter:
                self.interactivity=inter
            raise RuntimeError("ERROR: Some of the reification function behaviors were not saved. ")
        #try saving the function
        try:
            ReificationFunctionDB.__persist__(self)
        except:
            raise RuntimeError("ERROR: Not able to save the Reification Function: "+self.external_id)

    ############################# Setters and Removals (without perssistence)

    def add_mechanical_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.mechanical.add(element)
        self.elements.add(element)

    def discard_mechanical_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.mechanical:
            self.mechanical.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity) or (element in self.device))):
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
            if (not ((element in self.mechanical) or (element in self.device))):
                self.elements.discard(element)

    def add_device_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.device.add(element)
        self.elements.add(element)

    def discard_device_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.device:
            self.device.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity) or (element in self.mechanical))):
                self.elements.discard(element)

    def set_interactivity(self,interactivity_):
        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if interactivity_.behavior_type!="INTERACTIVITY":
            raise TypeError("ERROR! Assigning a Non INTERACTIVITY Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.interactivity.elements=interactivity_.elements


    def set_mechanical(self,mechanical_):
        if not isinstance(mechanical_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if mechanical_.behavior_type!="MECHANICAL":
            raise TypeError("ERROR! Assigning a Non mechanical Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.mechanical.elements=mechanical_.elements

    def set_device(self,device_):
        if not isinstance(device_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if device_.behavior_type!="DEVICE":
            raise TypeError("ERROR! Assigning a Non device Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.device.elements=device_.elements

    def reset_mechanical(self):
        self.mechanical.reset()
        
    def reset_interactivity(self):
        self.interactivity.reset()
        
    def reset_device(self):
        self.device.reset()

    #########################################################################

    ############################# Setters and Removals (with perssistence)

    def p_add_mechanical_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.mechanical.add(element)
        self.elements.add(element)
        self.mechanical.save()

    def p_discard_mechanical_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.mechanical:
            self.mechanical.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity) or (element in self.device))):
                self.elements.discard(element)
        self.mechanical.save()

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
            if (not ((element in self.mechanical) or (element in self.device))):
                self.elements.discard(element)
        self.interactivity.save()

    def p_add_device_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        self.device.add(element)
        self.elements.add(element)
        self.device.save()

    def p_discard_device_element(self, element):
        if not isinstance(element,ElementAO):
            raise TypeError("ERROR: Argument not a valid ElementAO object.")
        if element in self.device:
            self.device.discard(element)
            #need to check in the others to verify if remove from the set.
            if (not ((element in self.interactivity) or (element in self.mechanical))):
                self.elements.discard(element)
        self.device.save()

    def p_set_interactivity(self,interactivity_):
        if not isinstance(interactivity_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if interactivity_.behavior_type!="INTERACTIVITY":
            raise TypeError("ERROR! Assigning a Non INTERACTIVITY Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.interactivity.elements=interactivity_.elements
        self.interactivity.save()


    def p_set_mechanical(self,mechanical_):
        if not isinstance(mechanical_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if mechanical_.behavior_type!="MECHANICAL":
            raise TypeError("ERROR! Assigning a Non mechanical Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.mechanical.elements=mechanical_.elements
        self.mechanical.save()

    def p_set_gamegfication(self,device_):
        if not isinstance(device_,BehaviorAO):
            raise TypeError("ERROR! Argument is not a valid BehaviorAO object")
        if device_.behavior_type!="DEVICE":
            raise TypeError("ERROR! Assigning a Non device Behavior Type to Behavior Slot")
        #The set function does not properly replace the Behavior due to the External_id
        # it replaces only the Behavior Element List. This will be processed in the Diff when persisting.
        self.device.elements=device_.elements
        self.device.save()

    def p_reset_mechanical(self):
        self.mechanical.reset()
        self.mechanical.save()
        
    def p_reset_interactivity(self):
        self.interactivity.reset()
        self.interactivity.save()
        
    def p_reset_device(self):
        self.device.reset()
        self.device.save()
        

    #########################################################################

    def copy(self):
        """ 
            Create a copy of the data.
            The behaviors are created anew as well.
            There is no external ID, for none!
                TODO: Check the save method to verify proper assignments to this case!
        """
        to_ret=ReificationFunctionAO(self.interactivity.copy(), self.mechanical.copy(), self.device.copy())
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
            other {ReificationFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_subset=self.interactivity.issubset(other.interactivity)
        lud_subset=self.mechanical.issubset(other.mechanical)
        gam_subset=self.device.issubset(other.device)
        return int_subset and lud_subset and gam_subset

    def issuperset(self,other):
        """ Returns true only if every behavior is a superset of its related behavior in other
        
        Arguments:
            other {ReificationFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_superset=self.interactivity.issuperset(other.interactivity)
        lud_superset=self.mechanical.issuperset(other.mechanical)
        gam_superset=self.device.issuperset(other.device)
        return int_superset and lud_superset and gam_superset

    def isdisjoint(self,other):
        """ Return True only if there are no intersections between the related behaviors nor between the elements
        
        Arguments:
            other {ReificationFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_inter=self.interactivity & other.interactivity
        lud_inter=self.mechanical & other.mechanical
        gam_inter=self.device & other.device
        elem_inter=self.elements & other.elements
        return (not int_inter) and (not lud_inter) and (not gam_inter) and (not elem_inter)

    def isdisjoint_behavior(self,other):
        """ Return True only if there are no intersections only between the related behaviors 
        
        Arguments:
            other {ReificationFunctionAO} -- The object to compare
        """
        if not isinstance(other,self.__class__):
            raise TypeError("ERROR: Operand Type differs. They must be the same")
        int_inter=self.interactivity & other.interactivity
        lud_inter=self.mechanical & other.mechanical
        gam_inter=self.device & other.device
        return (not int_inter) and (not lud_inter) and (not gam_inter)

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
        if(el in self.mechanical):
            beh.append("mechanical")
        if(el in self.device):
            beh.append("device")
        self.discard(el)
        return {
            "element": el,
            "behavior": beh
        }

    for method in ['clear', 'difference_update', 'intersection_update', 'symmetric_difference_update', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.elements, method)(*((other,) if other else ()) ) ) (method)
