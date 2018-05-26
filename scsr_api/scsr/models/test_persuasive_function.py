import json
import unittest
from mongoengine.connection import _get_db
from scsr.models.elements import ElementAO, ElementDB, ElementReferenceDB, ElementReferenceAO, ElementGameMappingAO, ElementGameMappingDB
from scsr.models.behaviors import BehaviorAO, BehaviorDB
from scsr.models.persuasive_function import PersuasiveFunctionAO, PersuasiveFunctionDB
from application import ScsrAPP
from settings import MONGODB_HOST

"""Class to test the creation and relational mapping of the Persuasive Function

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

class PersuasiveFunctionModelTest(unittest.TestCase):
    
    func1 = None
    func2 = None

    elDB = None

    elAO  = None

    # The elements indexes to test
    inter = None
    ludi = None
    gamef = None
    mech = None
    devi  = None
    inter1 = None
    ludi1 = None
    gamef1 = None
    mech1  = None
    devi1  = None

    interbeh = None
    ludbeh = None
    mechbeh = None
    gamefbeh = None
    devibeh = None

    #The elements list for each operation to compare with the operated function
    interand = None
    interor = None
    interxor = None
    interdifference = None
    interunion = None
    interinter = None
    #The elements list for each operation to compare with the operated function
    ludand = None
    ludor = None
    ludxor = None
    luddifference = None
    ludunion = None
    ludinter = None
    #The elements list for each operation to compare with the operated function
    gamefand = None
    gamefor = None
    gamefxor = None
    gamefdifference = None
    gamefunion = None
    gamefinter = None
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

    ludbehand = None
    ludbehor = None
    ludbehxor = None
    ludbehdifference = None
    ludbehinter = None
    ludbehunion = None

    gamefbehand = None
    gamefbehor = None
    gamefbehxor = None
    gamefbehdifference = None
    gamefbehinter = None
    gamefbehunion = None

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
        cls.ludi=[5,6,7]
        cls.gamef=[8,9,10,11,12]
        cls.mech=[91,92,93,94]
        cls.devi = [101,102,103]
        cls.inter1=[1,3,41,42,43]
        cls.ludi1=[51,52,6,2]
        cls.gamef1=[61,62,63,64,65,11,4,7]
        cls.mech1 = [90,81,92,93,84]
        cls.devi1 = [201,202,101,104]

    @classmethod
    def init_elements(cls):

        cls.elDB=ElementDB.objects # pylint: disable=no-member

        cls.elAO = [el.to_obj() for el in cls.elDB]

        cls.interbeh = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.ludbeh = BehaviorAO(behavior_type="LUDIC")
        cls.gamefbeh = BehaviorAO(behavior_type="GAMEFICATION")
        cls.mechbeh = BehaviorAO(behavior_type="MECHANICAL")
        cls.devibeh = BehaviorAO(behavior_type="DEVICE")

        for el in cls.inter:
            cls.interbeh.add(cls.elAO[el])
        for el in cls.ludi:
            cls.ludbeh.add(cls.elAO[el])
        for el in cls.gamef:
            cls.gamefbeh.add(cls.elAO[el])
        for el in cls.mech:
            cls.mechbeh.add(cls.elAO[el])
        for el in cls.devi:
            cls.devibeh.add(cls.elAO[el])


        cls.interbeh2 = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.ludbeh2 = BehaviorAO(behavior_type="LUDIC")
        cls.gamefbeh2 = BehaviorAO(behavior_type="GAMEFICATION")
        cls.mechbeh2 = BehaviorAO(behavior_type="MECHANICAL")
        cls.devibeh2 = BehaviorAO(behavior_type="DEVICE")

        for el in cls.inter1:
            cls.interbeh2.add(cls.elAO[el])
        for el in cls.ludi1:
            cls.ludbeh2.add(cls.elAO[el])
        for el in cls.gamef1:
            cls.gamefbeh2.add(cls.elAO[el])
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
    def init_ludic_operated_indexes(cls):
        #The elements list for each operation to compare with the operated function
        cls.ludand=set(cls.ludi) & set(cls.ludi1)
        cls.ludor=set(cls.ludi) | set(cls.ludi1)
        cls.ludxor=set(cls.ludi) ^ set(cls.ludi1)
        cls.luddifference=set((set(cls.ludi) ^ set(cls.ludi1)) & set(cls.ludi))
        cls.ludunion=set(cls.ludi) | set(cls.ludi1)
        cls.ludinter=set(cls.ludi) & set(cls.ludi1)

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
    def init_gamefication_operated_indexes(cls):
        #The elements list for each operation to compare with the operated function
        cls.gamefand=set(cls.gamef) & set(cls.gamef1)
        cls.gamefor=set(cls.gamef) | set(cls.gamef1)
        cls.gamefxor=set(cls.gamef) ^ set(cls.gamef1)
        cls.gamefdifference=set((set(cls.gamef) ^ set(cls.gamef1)) & set(cls.gamef))
        cls.gamefunion=set(cls.gamef) | set(cls.gamef1)
        cls.gamefinter=set(cls.gamef) & set(cls.gamef1)

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
    def init_ludic_behavior_operand_comparators(cls):
        cls.ludbehand=BehaviorAO()
        cls.ludbehor=BehaviorAO()
        cls.ludbehxor=BehaviorAO()
        cls.ludbehdifference=BehaviorAO()
        cls.ludbehinter=BehaviorAO()
        cls.ludbehunion=BehaviorAO()
        for el in cls.ludand:
            cls.ludbehand.add(cls.elAO[el])

        for el in cls.ludor:
            cls.ludbehor.add(cls.elAO[el])

        for el in cls.ludxor:
            cls.ludbehxor.add(cls.elAO[el])

        for el in cls.luddifference:
            cls.ludbehdifference.add(cls.elAO[el])

        for el in cls.ludinter:
            cls.ludbehinter.add(cls.elAO[el])

        for el in cls.ludunion:
            cls.ludbehunion.add(cls.elAO[el])

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
    def init_gamefication_behavior_operand_comparators(cls):
        cls.gamefbehand=BehaviorAO()
        cls.gamefbehor=BehaviorAO()
        cls.gamefbehxor=BehaviorAO()
        cls.gamefbehdifference=BehaviorAO()
        cls.gamefbehinter=BehaviorAO()
        cls.gamefbehunion=BehaviorAO()
        for el in cls.gamefand:
            cls.gamefbehand.add(cls.elAO[el])

        for el in cls.gamefor:
            cls.gamefbehor.add(cls.elAO[el])

        for el in cls.gamefxor:
            cls.gamefbehxor.add(cls.elAO[el])

        for el in cls.gamefdifference:
            cls.gamefbehdifference.add(cls.elAO[el])

        for el in cls.gamefinter:
            cls.gamefbehinter.add(cls.elAO[el])

        for el in cls.gamefunion:
            cls.gamefbehunion.add(cls.elAO[el])

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
        print(" "*40+"Testing Persuasive Function Model")
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

        cls.init_ludic_operated_indexes()

        cls.init_mechanical_operated_indexes()

        cls.init_gamefication_operated_indexes()

        cls.init_device_operated_indexes()

        cls.init_interactivity_behavior_operand_comparators()

        cls.init_ludic_behavior_operand_comparators()

        cls.init_mechanical_behavior_operand_comparators()

        cls.init_gamefication_behavior_operand_comparators()
        
        cls.init_device_behavior_operand_comparators()


    @classmethod
    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)

    def setUp(self):
        pass

    def tearDown(self):
        pass


    #This test does not deals with APP
    def test_01(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf=PersuasiveFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf.interactivity
        l_ludbeh=pf.ludic
        l_gamefbeh=pf.gamefication
        assert pf.elements is not None
        assert pf.external_id is not None
        assert len(pf.external_id) > 0
        assert l_intbeh is not None
        assert l_ludbeh is not None
        assert l_gamefbeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_ludbeh.external_id is not None
        assert len(l_ludbeh.external_id) > 0
        assert l_gamefbeh.external_id is not None
        assert len(l_gamefbeh.external_id) > 0
        pfdb=PersuasiveFunctionDB.objects.filter(external_id=pf.external_id).first() # pylint: disable=no-member
        assert pfdb is not None
        assert pfdb.external_id == pf.external_id
        self.__class__.func1=pf.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        lbdb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        assert lbdb is not None
        assert lbdb.external_id == l_ludbeh.external_id
        gbdb=BehaviorDB.objects.filter(external_id=l_gamefbeh.external_id).first() # pylint: disable=no-member
        assert gbdb is not None
        assert gbdb.external_id == l_gamefbeh.external_id
        #By now: The function was created. Its behaviors as well. All persisted. All empty.

    def test_02(self):
        #add the elements to the persuasive function, persist and check
        #add the elements to each behavior
        pf=PersuasiveFunctionAO.get_function(self.func1)
        for elt in self.inter:
            pf.add_interactivity_element(self.elAO[elt])

        for elt in self.ludi:
            pf.add_ludic_element(self.elAO[elt])

        for elt in self.gamef:
            pf.add_gamefication_element(self.elAO[elt])
        #check each behavior (the hashes must be the same)
        assert pf.interactivity.issubset(self.interbeh) and pf.interactivity.issuperset(self.interbeh)
        assert pf.ludic.issubset(self.ludbeh) and pf.ludic.issuperset(self.ludbeh)
        assert pf.gamefication.issubset(self.gamefbeh) and pf.gamefication.issuperset(self.gamefbeh)
        #persist
        pf.save()
        #check persistence information
        l_intbeh=pf.interactivity
        l_ludbeh=pf.ludic
        l_gamefbeh=pf.gamefication
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        ldb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        gdb=BehaviorDB.objects.filter(external_id=l_gamefbeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf.interactivity.issubset(idb.to_obj()) and pf.interactivity.issuperset(idb.to_obj())
        assert pf.ludic.issubset(ldb.to_obj()) and pf.ludic.issuperset(ldb.to_obj())
        assert pf.gamefication.issubset(gdb.to_obj()) and pf.gamefication.issuperset(gdb.to_obj())
        



    #This test does not deals with APP
    def test_03(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf2=PersuasiveFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf2.interactivity
        l_ludbeh=pf2.ludic
        l_gamefbeh=pf2.gamefication
        assert pf2.elements is not None
        assert pf2.external_id is not None
        assert len(pf2.external_id) > 0
        assert l_intbeh is not None
        assert l_ludbeh is not None
        assert l_gamefbeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_ludbeh.external_id is not None
        assert len(l_ludbeh.external_id) > 0
        assert l_gamefbeh.external_id is not None
        assert len(l_gamefbeh.external_id) > 0
        pf2db=PersuasiveFunctionDB.objects.filter(external_id=pf2.external_id).first() # pylint: disable=no-member
        assert pf2db is not None
        assert pf2db.external_id == pf2.external_id
        self.__class__.func2=pf2.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        lbdb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        assert lbdb is not None
        assert lbdb.external_id == l_ludbeh.external_id
        gbdb=BehaviorDB.objects.filter(external_id=l_gamefbeh.external_id).first() # pylint: disable=no-member
        assert gbdb is not None
        assert gbdb.external_id == l_gamefbeh.external_id
        #By now: The function was created. Its behaviors as well. All persisted. All empty.

    def test_04(self):
        #add the elements to the persuasive function, persist and check
        #add the elements to each behavior
        pf2=PersuasiveFunctionAO.get_function(self.func2)
        for elt in self.inter1:
            pf2.add_interactivity_element(self.elAO[elt])

        for elt in self.ludi1:
            pf2.add_ludic_element(self.elAO[elt])

        for elt in self.gamef1:
            pf2.add_gamefication_element(self.elAO[elt])
        #check each behavior (the hashes must be the same)
        assert pf2.interactivity.issubset(self.interbeh2) and pf2.interactivity.issuperset(self.interbeh2)
        assert pf2.ludic.issubset(self.ludbeh2) and pf2.ludic.issuperset(self.ludbeh2)
        assert pf2.gamefication.issubset(self.gamefbeh2) and pf2.gamefication.issuperset(self.gamefbeh2)
        #persist
        pf2.save()
        #check persistence information
        l_intbeh=pf2.interactivity
        l_ludbeh=pf2.ludic
        l_gamefbeh=pf2.gamefication
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        ldb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        gdb=BehaviorDB.objects.filter(external_id=l_gamefbeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf2.interactivity.issubset(idb.to_obj()) and pf2.interactivity.issuperset(idb.to_obj())
        assert pf2.ludic.issubset(ldb.to_obj()) and pf2.ludic.issuperset(ldb.to_obj())
        assert pf2.gamefication.issubset(gdb.to_obj()) and pf2.gamefication.issuperset(gdb.to_obj())
        

    def test_05(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf & pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehand) and pf3.interactivity.issuperset(self.interbehand)
        assert pf3.ludic.issubset(self.ludbehand) and pf3.ludic.issuperset(self.ludbehand)
        assert pf3.gamefication.issubset(self.gamefbehand) and pf3.gamefication.issuperset(self.gamefbehand)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_06(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf | pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehor) and pf3.interactivity.issuperset(self.interbehor)
        assert pf3.ludic.issubset(self.ludbehor) and pf3.ludic.issuperset(self.ludbehor)
        assert pf3.gamefication.issubset(self.gamefbehor) and pf3.gamefication.issuperset(self.gamefbehor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)

    
    def test_07(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf ^ pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehxor) and pf3.interactivity.issuperset(self.interbehxor)
        assert pf3.ludic.issubset(self.ludbehxor) and pf3.ludic.issuperset(self.ludbehxor)
        assert pf3.gamefication.issubset(self.gamefbehxor) and pf3.gamefication.issuperset(self.gamefbehxor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_08(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf - pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehdifference) and pf3.interactivity.issuperset(self.interbehdifference)
        assert pf3.ludic.issubset(self.ludbehdifference) and pf3.ludic.issuperset(self.ludbehdifference)
        assert pf3.gamefication.issubset(self.gamefbehdifference) and pf3.gamefication.issuperset(self.gamefbehdifference)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_09(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.intersection(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehinter) and pf3.interactivity.issuperset(self.interbehinter)
        assert pf3.ludic.issubset(self.ludbehinter) and pf3.ludic.issuperset(self.ludbehinter)
        assert pf3.gamefication.issubset(self.gamefbehinter) and pf3.gamefication.issuperset(self.gamefbehinter)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_10(self):
        #retrieve persisted function
        pf=PersuasiveFunctionAO.get_function(self.func1)

        pf2=PersuasiveFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.union(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehunion) and pf3.interactivity.issuperset(self.interbehunion)
        assert pf3.ludic.issubset(self.ludbehunion) and pf3.ludic.issuperset(self.ludbehunion)
        assert pf3.gamefication.issubset(self.gamefbehunion) and pf3.gamefication.issuperset(self.gamefbehunion)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


if __name__ =='__main__':
    unittest.main()