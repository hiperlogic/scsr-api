import json
import unittest
from mongoengine.connection import _get_db
from scsr.models.elements import ElementAO, ElementDB, ElementReferenceDB, ElementReferenceAO, ElementGameMappingAO, ElementGameMappingDB
from scsr.models.behaviors import BehaviorAO, BehaviorDB
from scsr.models.reification_function import ReificationFunctionAO, ReificationFunctionDB
from application import ScsrAPP
from settings import MONGODB_HOST

"""Class to test the creation and relational mapping of the Reification Function

    The tests consist of:
        Creating a function
        adding elements
        verifying persistence
        Seeking function
        Creating another function
        add, persist and check the second function
        operate the first with the second in
        and
        or
        xor
        difference
        intersection
        union
        Reset the function and check the data.
"""

class ReificationFunctionModelTest(unittest.TestCase):
    
    func1 = None
    func2 = None

    elDB = None

    elAO  = None

    # The elements indexes to test
    inter = None
    mech = None
    devi  = None
    inter1 = None
    mech1  = None
    devi1  = None

    interbeh = None
    mechbeh = None
    devibeh = None

    #The elements list for each operation to compare with the operated function
    interand = None
    interor = None
    interxor = None
    interdifference = None
    interunion = None
    interinter = None

    #The elements list for each operation to compare with the operated function
    mechand = None
    mechor = None
    mechxor = None
    mechdifference = None
    mechunion = None
    mechinter = None
    #The elements list for each operation to compare with the operated function
    deviand = None
    devior = None
    devixor = None
    devidifference = None
    deviunion = None
    deviinter = None

    interbehand = None
    interbehor = None
    interbehxor = None
    interbehdifference = None
    interbehinter = None
    interbehunion = None


    mechbehand = None
    mechbehor = None
    mechbehxor = None
    mechbehdifference = None
    mechbehinter = None
    mechbehunion = None

    devibehand = None
    devibehor = None
    devibehxor = None
    devibehdifference = None
    devibehinter = None
    devibehunion = None


    @classmethod
    def init_indexes(cls):
        # The elements indexes to test
        cls.inter=[1,2,3,4]
        cls.mech=[91,92,93,94]
        cls.devi = [101,102,103]
        cls.inter1=[1,3,41,42,43]
        cls.mech1 = [90,81,92,93,84]
        cls.devi1 = [201,202,101,104]

    @classmethod
    def init_elements(cls):

        cls.elDB=ElementDB.objects # pylint: disable=no-member

        cls.elAO = [el.to_obj() for el in cls.elDB]

        cls.interbeh = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.mechbeh = BehaviorAO(behavior_type="MECHANICAL")
        cls.devibeh = BehaviorAO(behavior_type="DEVICE")

        for el in cls.inter:
            cls.interbeh.add(cls.elAO[el])
        for el in cls.mech:
            cls.mechbeh.add(cls.elAO[el])
        for el in cls.devi:
            cls.devibeh.add(cls.elAO[el])

        cls.interbeh2 = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.mechbeh2 = BehaviorAO(behavior_type="MECHANICAL")
        cls.devibeh2 = BehaviorAO(behavior_type="DEVICE")

        for el in cls.inter1:
            cls.interbeh2.add(cls.elAO[el])
        for el in cls.mech1:
            cls.mechbeh2.add(cls.elAO[el])
        for el in cls.devi1:
            cls.devibeh2.add(cls.elAO[el])

    
    @classmethod
    def init_interactivity_operated_indexes(cls):
        #The elements list for each operation to compare with the operated function
        cls.interand=set(cls.inter) & set(cls.inter1)
        cls.interor=set(cls.inter) | set(cls.inter1)
        cls.interxor=set(cls.inter) ^ set(cls.inter1)
        cls.interdifference=set((set(cls.inter) ^ set(cls.inter1)) & set(cls.inter))
        cls.interunion=set(cls.inter) | set(cls.inter1)
        cls.interinter=set(cls.inter) & set(cls.inter1)

    @classmethod
    def init_mechanical_operated_indexes(cls):
        #The elements list for each operation to compare with the operated function
        cls.mechand=set(cls.mech) & set(cls.mech1)
        cls.mechor=set(cls.mech) | set(cls.mech1)
        cls.mechxor=set(cls.mech) ^ set(cls.mech1)
        cls.mechdifference=set((set(cls.mech) ^ set(cls.mech1)) & set(cls.mech))
        cls.mechunion=set(cls.mech) | set(cls.mech1)
        cls.mechinter=set(cls.mech) & set(cls.mech1)
    
    @classmethod
    def init_device_operated_indexes(cls):
        #The elements list for each operation to compare with the operated function
        cls.deviand=set(cls.devi) & set(cls.devi1)
        cls.devior=set(cls.devi) | set(cls.devi1)
        cls.devixor=set(cls.devi) ^ set(cls.devi1)
        cls.devidifference=set((set(cls.devi) ^ set(cls.devi1)) & set(cls.devi))
        cls.deviunion=set(cls.devi) | set(cls.devi1)
        cls.deviinter=set(cls.devi) & set(cls.devi1)

    @classmethod
    def init_interactivity_behavior_operand_comparators(cls):
        cls.interbehand = BehaviorAO()
        cls.interbehor = BehaviorAO()
        cls.interbehxor = BehaviorAO()
        cls.interbehdifference = BehaviorAO()
        cls.interbehinter = BehaviorAO()
        cls.interbehunion = BehaviorAO()

        for el in cls.interand:
            cls.interbehand.add(cls.elAO[el])

        for el in cls.interor:
            cls.interbehor.add(cls.elAO[el])

        for el in cls.interxor:
            cls.interbehxor.add(cls.elAO[el])

        for el in cls.interdifference:
            cls.interbehdifference.add(cls.elAO[el])

        for el in cls.interinter:
            cls.interbehinter.add(cls.elAO[el])

        for el in cls.interunion:
            cls.interbehunion.add(cls.elAO[el])


    @classmethod
    def init_mechanical_behavior_operand_comparators(cls):
        cls.mechbehand=BehaviorAO()
        cls.mechbehor=BehaviorAO()
        cls.mechbehxor=BehaviorAO()
        cls.mechbehdifference=BehaviorAO()
        cls.mechbehinter=BehaviorAO()
        cls.mechbehunion=BehaviorAO()
        for el in cls.mechand:
            cls.mechbehand.add(cls.elAO[el])

        for el in cls.mechor:
            cls.mechbehor.add(cls.elAO[el])

        for el in cls.mechxor:
            cls.mechbehxor.add(cls.elAO[el])

        for el in cls.mechdifference:
            cls.mechbehdifference.add(cls.elAO[el])

        for el in cls.mechinter:
            cls.mechbehinter.add(cls.elAO[el])

        for el in cls.mechunion:
            cls.mechbehunion.add(cls.elAO[el])

    @classmethod
    def init_device_behavior_operand_comparators(cls):
        cls.devibehand=BehaviorAO()
        cls.devibehor=BehaviorAO()
        cls.devibehxor=BehaviorAO()
        cls.devibehdifference=BehaviorAO()
        cls.devibehinter=BehaviorAO()
        cls.devibehunion=BehaviorAO()
        for el in cls.deviand:
            cls.devibehand.add(cls.elAO[el])

        for el in cls.devior:
            cls.devibehor.add(cls.elAO[el])

        for el in cls.devixor:
            cls.devibehxor.add(cls.elAO[el])

        for el in cls.devidifference:
            cls.devibehdifference.add(cls.elAO[el])

        for el in cls.deviinter:
            cls.devibehinter.add(cls.elAO[el])

        for el in cls.deviunion:
            cls.devibehunion.add(cls.elAO[el])

    @classmethod
    def setUpClass(cls):
        print("*"*130)
        print(" "*40+"Testing Reification Function Model")
        print("*"*130)
        cls.db_name = 'scsr-api-test2'
        
        cls.app_factory = ScsrAPP(
            MONGODB_SETTINGS = {'DB': cls.db_name,
                'HOST': MONGODB_HOST},
            TESTING = True,
            WTF_CSRF_ENABLED = False,
            SECRET_KEY = 'mySecret!').APP
        cls.app = cls.app_factory.test_client()
        #initialize the database with the countries and languages
        from install_system import start_countries,start_language, start_games, start_genre, start_elements_ontology, start_elements_pigd

        start_countries()
        start_language()
        start_genre()
        start_games()
        start_elements_ontology()
        start_elements_pigd()
        #load the elements
        cls.init_indexes()

        cls.init_elements()

        cls.init_interactivity_operated_indexes()

        cls.init_mechanical_operated_indexes()

        cls.init_device_operated_indexes()

        cls.init_device_behavior_operand_comparators()

        cls.init_mechanical_behavior_operand_comparators()

        cls.init_interactivity_behavior_operand_comparators()


    @classmethod
    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)


    def setUp(self):
        pass

    def tearDown(self):
        pass


    #This test does not deals with APP
    '''     def test_reification_function_create_class(self):
    '''    
    def test_01(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf=ReificationFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf.interactivity
        l_devibeh=pf.device
        l_mechbeh=pf.mechanical
        assert pf.elements is not None
        assert pf.external_id is not None
        assert len(pf.external_id) > 0
        assert l_intbeh is not None
        assert l_devibeh is not None
        assert l_mechbeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_devibeh.external_id is not None
        assert len(l_devibeh.external_id) > 0
        assert l_mechbeh.external_id is not None
        assert len(l_mechbeh.external_id) > 0
        pfdb=ReificationFunctionDB.objects.filter(external_id=pf.external_id).first() # pylint: disable=no-member
        assert pfdb is not None
        assert pfdb.external_id == pf.external_id
        self.__class__.func1=pf.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        dbdb=BehaviorDB.objects.filter(external_id=l_devibeh.external_id).first() # pylint: disable=no-member
        assert dbdb is not None
        assert dbdb.external_id == l_devibeh.external_id
        mbdb=BehaviorDB.objects.filter(external_id=l_mechbeh.external_id).first() # pylint: disable=no-member
        assert mbdb is not None
        assert mbdb.external_id == l_mechbeh.external_id
        #By now: The function was created. Its behaviors as well. All persisted. All empty.

    ''' def test_reification_function_element_add(self): '''
    def test_02(self):
        #add the elements to the reification function, persist and check
        #add the elements to each behavior
        pf=ReificationFunctionAO.get_function(self.func1)
        for elt in self.inter:
            pf.add_interactivity_element(self.elAO[elt])

        for elt in self.mech:
            pf.add_mechanical_element(self.elAO[elt])

        for elt in self.devi:
            pf.add_device_element(self.elAO[elt])
        #check each behavior (the hashes must be the same)
        assert pf.interactivity.issubset(self.interbeh) and pf.interactivity.issuperset(self.interbeh)
        assert pf.mechanical.issubset(self.mechbeh) and pf.mechanical.issuperset(self.mechbeh)
        assert pf.device.issubset(self.devibeh) and pf.device.issuperset(self.devibeh)
        #persist
        pf.save()
        #check persistence information
        l_intbeh=pf.interactivity
        l_mechbeh=pf.mechanical
        l_devibeh=pf.device
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        mdb=BehaviorDB.objects.filter(external_id=l_mechbeh.external_id).first() # pylint: disable=no-member
        ddb=BehaviorDB.objects.filter(external_id=l_devibeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf.interactivity.issubset(idb.to_obj()) and pf.interactivity.issuperset(idb.to_obj())
        assert pf.mechanical.issubset(mdb.to_obj()) and pf.mechanical.issuperset(mdb.to_obj())
        assert pf.device.issubset(ddb.to_obj()) and pf.device.issuperset(ddb.to_obj())
        



    #This test does not deals with APP
    ''' def test_reification_function_operand_create_class(self): '''
    def test_03(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf2=ReificationFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf2.interactivity
        l_mechbeh=pf2.mechanical
        l_devibeh=pf2.device
        assert pf2.elements is not None
        assert pf2.external_id is not None
        assert len(pf2.external_id) > 0
        assert l_intbeh is not None
        assert l_mechbeh is not None
        assert l_devibeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_mechbeh.external_id is not None
        assert len(l_mechbeh.external_id) > 0
        assert l_devibeh.external_id is not None
        assert len(l_devibeh.external_id) > 0
        pf2db=ReificationFunctionDB.objects.filter(external_id=pf2.external_id).first() # pylint: disable=no-member
        assert pf2db is not None
        assert pf2db.external_id == pf2.external_id
        self.__class__.func2=pf2.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        mbdb=BehaviorDB.objects.filter(external_id=l_mechbeh.external_id).first() # pylint: disable=no-member
        assert mbdb is not None
        assert mbdb.external_id == l_mechbeh.external_id
        dbdb=BehaviorDB.objects.filter(external_id=l_devibeh.external_id).first() # pylint: disable=no-member
        assert dbdb is not None
        assert dbdb.external_id == l_devibeh.external_id
        #By now: The function was created. Its behaviors as well. All persisted. All empty.

    ''' def test_reification_function_operand_element_add(self): '''
    def test_04(self):
        #add the elements to the reification function, persist and check
        #add the elements to each behavior
        pf2=ReificationFunctionAO.get_function(self.func2)
        for elt in self.inter1:
            pf2.add_interactivity_element(self.elAO[elt])

        for elt in self.mech1:
            pf2.add_mechanical_element(self.elAO[elt])

        for elt in self.devi1:
            pf2.add_device_element(self.elAO[elt])
        #check each behavior (the hashes must be the same)
        assert pf2.interactivity.issubset(self.interbeh2) and pf2.interactivity.issuperset(self.interbeh2)
        assert pf2.mechanical.issubset(self.mechbeh2) and pf2.mechanical.issuperset(self.mechbeh2)
        assert pf2.device.issubset(self.devibeh2) and pf2.device.issuperset(self.devibeh2)
        #persist
        pf2.save()
        #check persistence information
        l_intbeh=pf2.interactivity
        l_mechbeh=pf2.mechanical
        l_devibeh=pf2.device
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        mdb=BehaviorDB.objects.filter(external_id=l_mechbeh.external_id).first() # pylint: disable=no-member
        ddb=BehaviorDB.objects.filter(external_id=l_devibeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf2.interactivity.issubset(idb.to_obj()) and pf2.interactivity.issuperset(idb.to_obj())
        assert pf2.mechanical.issubset(mdb.to_obj()) and pf2.mechanical.issuperset(mdb.to_obj())
        assert pf2.device.issubset(ddb.to_obj()) and pf2.device.issuperset(ddb.to_obj())
        

    ''' def test_reification_and(self): '''
    def test_05(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf & pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehand) and pf3.interactivity.issuperset(self.interbehand)
        assert pf3.mechanical.issubset(self.mechbehand) and pf3.mechanical.issuperset(self.mechbehand)
        assert pf3.device.issubset(self.devibehand) and pf3.device.issuperset(self.devibehand)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    ''' def test_reification_or(self): '''
    def test_06(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf | pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehor) and pf3.interactivity.issuperset(self.interbehor)
        assert pf3.mechanical.issubset(self.mechbehor) and pf3.mechanical.issuperset(self.mechbehor)
        assert pf3.device.issubset(self.devibehor) and pf3.device.issuperset(self.devibehor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)

    
    ''' def test_reification_xor(self): '''
    def test_07(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf ^ pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehxor) and pf3.interactivity.issuperset(self.interbehxor)
        assert pf3.mechanical.issubset(self.mechbehxor) and pf3.mechanical.issuperset(self.mechbehxor)
        assert pf3.device.issubset(self.devibehxor) and pf3.device.issuperset(self.devibehxor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,pf3.save)


    ''' def test_reification_difference(self): '''
    def test_08(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf - pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehdifference) and pf3.interactivity.issuperset(self.interbehdifference)
        assert pf3.mechanical.issubset(self.mechbehdifference) and pf3.mechanical.issuperset(self.mechbehdifference)
        assert pf3.device.issubset(self.devibehdifference) and pf3.device.issuperset(self.devibehdifference)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,pf3.save)


    ''' def test_reification_intersection(self): '''
    def test_09(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.intersection(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehinter) and pf3.interactivity.issuperset(self.interbehinter)
        assert pf3.mechanical.issubset(self.mechbehinter) and pf3.mechanical.issuperset(self.mechbehinter)
        assert pf3.device.issubset(self.devibehinter) and pf3.device.issuperset(self.devibehinter)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,pf3.save)


    ''' def test_reification_union(self): '''
    def test_10(self):
        #retrieve persisted function
        pf=ReificationFunctionAO.get_function(self.func1)

        pf2=ReificationFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.union(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehunion) and pf3.interactivity.issuperset(self.interbehunion)
        assert pf3.mechanical.issubset(self.mechbehunion) and pf3.mechanical.issuperset(self.mechbehunion)
        assert pf3.device.issubset(self.devibehunion) and pf3.device.issuperset(self.devibehunion)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,pf3.save)


if __name__ =='__main__':
    unittest.main()