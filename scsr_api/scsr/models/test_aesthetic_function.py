import json
import unittest
from mongoengine.connection import _get_db
from scsr.models.elements import ElementAO, ElementDB, ElementReferenceDB, ElementReferenceAO, ElementGameMappingAO, ElementGameMappingDB
from scsr.models.behaviors import BehaviorAO, BehaviorDB
from scsr.models.aesthetic_function import AestheticFunctionAO, AestheticFunctionDB
from application import ScsrAPP
from settings import MONGODB_HOST

"""Class to test the creation and relational mapping of the Aesthetic Function

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

class AestheticFunctionModelTest(unittest.TestCase):
    
    func1 = None
    func2 = None

    elDB = None

    elAO  = None

    # The elements indexes to test
    inter = None
    ludi = None
    inter1 = None
    ludi1 = None

    interbeh = None
    ludbeh = None

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

    @classmethod
    def init_indexes(cls):
        # The elements indexes to test
        cls.inter=[1,2,3,4]
        cls.ludi=[5,6,7]
        cls.inter1=[1,3,41,42,43]
        cls.ludi1=[51,52,6,2]

    @classmethod
    def init_elements(cls):

        cls.elDB=ElementDB.objects # pylint: disable=no-member

        cls.elAO = [el.to_obj() for el in cls.elDB]

        cls.interbeh = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.ludbeh = BehaviorAO(behavior_type="LUDIC")

        for el in cls.inter:
            cls.interbeh.add(cls.elAO[el])
        for el in cls.ludi:
            cls.ludbeh.add(cls.elAO[el])

        cls.interbeh2 = BehaviorAO(behavior_type="INTERACTIVITY")
        cls.ludbeh2 = BehaviorAO(behavior_type="LUDIC")

        for el in cls.inter1:
            cls.interbeh2.add(cls.elAO[el])
        for el in cls.ludi1:
            cls.ludbeh2.add(cls.elAO[el])

    
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

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        print("*"*130)
        print(" "*40+"Testing Aesthetic Function Model")
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

        cls.init_interactivity_behavior_operand_comparators()

        cls.init_ludic_behavior_operand_comparators()

    @classmethod
    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)



    #This test does not deals with APP
    def test_01(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf=AestheticFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf.interactivity
        l_ludbeh=pf.ludic
        assert pf.elements is not None
        assert pf.external_id is not None
        assert len(pf.external_id) > 0
        assert l_intbeh is not None
        assert l_ludbeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_ludbeh.external_id is not None
        assert len(l_ludbeh.external_id) > 0
        pfdb=AestheticFunctionDB.objects.filter(external_id=pf.external_id).first() # pylint: disable=no-member
        assert pfdb is not None
        assert pfdb.external_id == pf.external_id
        self.__class__.func1=pf.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        lbdb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        assert lbdb is not None
        assert lbdb.external_id == l_ludbeh.external_id
        #By now: The function was created. Its behaviors as well. All persisted. All empty.

    def test_02(self):
        #add the elements to the aesthetic function, persist and check
        #add the elements to each behavior
        pf=AestheticFunctionAO.get_function(self.func1)
        for elt in self.inter:
            pf.add_interactivity_element(self.elAO[elt])

        for elt in self.ludi:
            pf.add_ludic_element(self.elAO[elt])

        #check each behavior (the hashes must be the same)
        assert pf.interactivity.issubset(self.interbeh) and pf.interactivity.issuperset(self.interbeh)
        assert pf.ludic.issubset(self.ludbeh) and pf.ludic.issuperset(self.ludbeh)
        #persist
        pf.save()
        #check persistence information
        l_intbeh=pf.interactivity
        l_ludbeh=pf.ludic
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        ldb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf.interactivity.issubset(idb.to_obj()) and pf.interactivity.issuperset(idb.to_obj())
        assert pf.ludic.issubset(ldb.to_obj()) and pf.ludic.issuperset(ldb.to_obj())
        



    #This test does not deals with APP
    def test_03(self):
        """
            Creating a function must start the behaviors and persist them
        """
        #creates the function...
        pf2=AestheticFunctionAO.create_function()
        #now, checks the persistence of each behavior
        l_intbeh=pf2.interactivity
        l_ludbeh=pf2.ludic
        assert pf2.elements is not None
        assert pf2.external_id is not None
        assert len(pf2.external_id) > 0
        assert l_intbeh is not None
        assert l_ludbeh is not None
        assert l_intbeh.external_id is not None
        assert len(l_intbeh.external_id) > 0
        assert l_ludbeh.external_id is not None
        assert len(l_ludbeh.external_id) > 0
        pf2db=AestheticFunctionDB.objects.filter(external_id=pf2.external_id).first() # pylint: disable=no-member
        assert pf2db is not None
        assert pf2db.external_id == pf2.external_id
        self.__class__.func2=pf2.external_id

        ibdb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        assert ibdb is not None
        assert ibdb.external_id == l_intbeh.external_id
        lbdb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        assert lbdb is not None
        assert lbdb.external_id == l_ludbeh.external_id

    def test_04(self):
        #add the elements to the aesthetic function, persist and check
        #add the elements to each behavior
        pf2=AestheticFunctionAO.get_function(self.func2)
        for elt in self.inter1:
            pf2.add_interactivity_element(self.elAO[elt])

        for elt in self.ludi1:
            pf2.add_ludic_element(self.elAO[elt])

        #check each behavior (the hashes must be the same)
        assert pf2.interactivity.issubset(self.interbeh2) and pf2.interactivity.issuperset(self.interbeh2)
        assert pf2.ludic.issubset(self.ludbeh2) and pf2.ludic.issuperset(self.ludbeh2)
        #persist
        pf2.save()
        #check persistence information
        l_intbeh=pf2.interactivity
        l_ludbeh=pf2.ludic
        idb=BehaviorDB.objects.filter(external_id=l_intbeh.external_id).first() # pylint: disable=no-member
        ldb=BehaviorDB.objects.filter(external_id=l_ludbeh.external_id).first() # pylint: disable=no-member
        #check each behavior persistence
        assert pf2.interactivity.issubset(idb.to_obj()) and pf2.interactivity.issuperset(idb.to_obj())
        assert pf2.ludic.issubset(ldb.to_obj()) and pf2.ludic.issuperset(ldb.to_obj())
        

    def test_05(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf & pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehand) and pf3.interactivity.issuperset(self.interbehand)
        assert pf3.ludic.issubset(self.ludbehand) and pf3.ludic.issuperset(self.ludbehand)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_06(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf | pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehor) and pf3.interactivity.issuperset(self.interbehor)
        assert pf3.ludic.issubset(self.ludbehor) and pf3.ludic.issuperset(self.ludbehor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)

    
    def test_07(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf ^ pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehxor) and pf3.interactivity.issuperset(self.interbehxor)
        assert pf3.ludic.issubset(self.ludbehxor) and pf3.ludic.issuperset(self.ludbehxor)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_08(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf - pf2
        #check the result
        assert pf3.interactivity.issubset(self.interbehdifference) and pf3.interactivity.issuperset(self.interbehdifference)
        assert pf3.ludic.issubset(self.ludbehdifference) and pf3.ludic.issuperset(self.ludbehdifference)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_09(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.intersection(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehinter) and pf3.interactivity.issuperset(self.interbehinter)
        assert pf3.ludic.issubset(self.ludbehinter) and pf3.ludic.issuperset(self.ludbehinter)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)


    def test_10(self):
        #retrieve persisted function
        pf=AestheticFunctionAO.get_function(self.func1)

        pf2=AestheticFunctionAO.get_function(self.func2)

        #perform the and operation
        pf3 = pf.union(pf2)
        #check the result
        assert pf3.interactivity.issubset(self.interbehunion) and pf3.interactivity.issuperset(self.interbehunion)
        assert pf3.ludic.issubset(self.ludbehunion) and pf3.ludic.issuperset(self.ludbehunion)
        assert pf3.external_id is None
        #try to persist (must fail!)
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError, pf3.save)

if __name__ =='__main__':
    unittest.main()