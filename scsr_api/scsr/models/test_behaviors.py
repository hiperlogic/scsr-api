import json
import unittest
from mongoengine.connection import _get_db
from scsr.models.elements import ElementAO, ElementDB, ElementReferenceDB, ElementReferenceAO, ElementGameMappingAO, ElementGameMappingDB
from scsr.models.behaviors import BehaviorAO, BehaviorDB
from application import ScsrAPP
from settings import MONGODB_HOST
class BehaviorModelTest(unittest.TestCase):
    
    @classmethod
    def init_elements(cls):

        cls.elDB=ElementDB.objects # pylint: disable=no-member
        cls.elAO = [el.to_obj() for el in cls.elDB]


    @classmethod
    def setUpClass(cls):
        print("*"*130)
        print(" "*40+"Testing Behavior Model")
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
        cls.els1=[1,3,5,7,9]
        cls.els2=[2,3,4,7,8,10,12,11]
        cls.els1_add=[6,13,18]
        cls.els1_rem1=[3]
        cls.els1_rem2=[5,9]
        cls.els1_add2=[20,24,32,42]
        cls.int=list(set(cls.els1) & set(cls.els2))
        cls.uni=list(set(cls.els1) | set(cls.els2))
        cls.xor=list(set(cls.els1) ^ set(cls.els2))
        cls.diff1=list(set(cls.els1) - set(cls.els2))
        cls.diff2=list(set(cls.els2) - set(cls.els1))
        cls.newels1=list(set(set(cls.els1) | set(cls.els1_add)) - set(cls.els1_rem1))
        cls.newels2=list(set(cls.newels1) - set(cls.els1_rem2) | set(cls.els1_add2)) 
        cls.init_elements()
        #load the elements

    @classmethod
    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)

    def test_01(self):
        """[summary]
            Create a behavior (store the external_id)
            Validation: Database accuses 1 behavior
        """
        print("test_01")
        beh1=BehaviorAO.create_behavior("LUDIC")
        assert beh1.external_id is not None
        assert BehaviorDB.objects.count() == 1 # pylint: disable=no-member
        for idx in self.els1:
            beh1.add(self.elAO[idx])
        beh1.save()
        assert len(beh1) == len(self.els1)
        self.__class__.eid1=beh1.external_id

    def test_02(self):
        print("test_02")
        """[summary]
            Create a second behavior, of the same type as the 1st (store the external_id)
            Validation: Database accuses 2 behavior
        """
        beh2=BehaviorAO.create_behavior("LUDIC")
        assert beh2.external_id is not None
        assert BehaviorDB.objects.count() == 2 # pylint: disable=no-member
        for idx in self.els2:
            beh2.add(self.elAO[idx])
        beh2.save()
        assert len(beh2) == len(self.els2)
        self.__class__.eid2=beh2.external_id
        pass

    def test_03(self):
        print("test_03")
        """[summary]
            Create a third behavior, of the different type as the 1st (store the external_id)
            Validation: Database accuses 3 behavior
        """
        behMec=BehaviorAO.create_behavior("MECHANICAL")
        assert behMec.external_id is not None
        assert BehaviorDB.objects.count() == 3 # pylint: disable=no-member
        for idx in self.els2:
            behMec.add(self.elAO[idx])
        behMec.save()
        assert len(behMec) == len(self.els2)
        self.__class__.eidMech=behMec.external_id
        

    def test_04(self):
        print("test_04")
        """[summary]
            And test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1 & beh2
        assert beh3.external_id == ""
        assert len(beh3) == len(self.int)
        assert beh3.behavior_type=="LUDIC"
        for el in self.int:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) and (el in beh1))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)


    def test_05(self):
        print("test_05")
        """[summary]
            Or test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1 | beh2
        assert beh3.external_id == ""
        assert len(beh3) == len(self.uni)
        assert beh3.behavior_type=="LUDIC"
        for el in self.uni:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) or (el in beh1))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)


    def test_06(self):
        print("test_06")
        """[summary]
            xor test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1 ^ beh2
        assert beh3.external_id == ""
        assert len(beh3) == len(self.xor)
        assert beh3.behavior_type=="LUDIC"
        for el in self.xor:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) and (not (el in beh1))) or ((el in beh1) and (not (el in beh2)))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)

    def test_07(self):
        print("test_07")
        """[summary]
            difference test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1.difference(beh2)
        assert beh3.external_id == ""
        assert len(beh3) == len(self.diff1)
        assert beh3.behavior_type=="LUDIC"
        for el in self.diff1:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh1) and (not (el in beh2)))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)

    def test_07_1(self):
        print("test_07_1")
        """[summary]
            difference test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh2.difference(beh1)
        assert beh3.external_id == ""
        assert len(beh3) == len(self.diff2)
        assert beh3.behavior_type=="LUDIC"
        for el in self.diff2:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) and (not (el in beh1)))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)

    def test_08(self):
        print("test_08")
        """[summary]
            intersection test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1.intersection(beh2)
        assert beh3.external_id == ""
        assert len(beh3) == len(self.int)
        assert beh3.behavior_type=="LUDIC"
        for el in self.int:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) and (el in beh1))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)

    def test_09(self):
        print("test_09")
        """[summary]
            union test
        """
        """[summary]
            Or test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1.union(beh2)
        assert beh3.external_id == ""
        assert len(beh3) == len(self.uni)
        assert beh3.behavior_type=="LUDIC"
        for el in self.uni:
            assert self.elAO[el] in beh3
        for el in beh3.elements:
            assert ((el in beh2) or (el in beh1))
        erro,msg=beh3.check_save()
        assert erro is RuntimeError
        self.assertRaises(RuntimeError, beh3.save)

    def test_10(self):
        print("test_10")
        """[summary]
            add more elements to 1st behavior
            Validation: Check out the diffs
        """
        """[summary]
            retrieve the 1st behavior add update elements to generate a diff
            Validation: Database behavior list of elements must be equal to the added
            Validation: Diff length must increase in 1
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        currdiffdata=beh1.diffdata
        for el in self.els1_add:
            beh1.add(self.elAO[el])
        for el in self.els1_rem1:
            beh1.discard(self.elAO[el])
        beh1.save()
        assert len(beh1.diffdata) == (len(currdiffdata)+1)
        for el in self.els1_add:
            assert self.elAO[el] in beh1
        for el in self.els1_rem1:
            assert self.elAO[el] not in beh1

    def test_10_1(self):
        print("test_10_1")
        """[summary]
            add more elements to 1st behavior
            Validation: Check out the diffs
        """
        """[summary]
            retrieve the 1st behavior add update elements to generate a diff
            Validation: Database behavior list of elements must be equal to the added
            Validation: Diff length must increase in 1
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        currdiffdata=beh1.diffdata
        for el in self.els1_add2:
            beh1.add(self.elAO[el])
        for el in self.els1_rem2:
            beh1.discard(self.elAO[el])
        beh1.save()
        assert len(beh1.diffdata) == (len(currdiffdata)+1)
        for el in self.els1_add2:
            assert self.elAO[el] in beh1
        for el in self.els1_rem2:
            assert self.elAO[el] not in beh1

    def test_11(self):
        print("test_11")
        """[summary]
            Add two behaviors
            Validation: Quantification test.
        """
        """[summary]
            union test
        """
        """[summary]
            Or test
        """
        beh1=BehaviorAO.get_behavior(self.eid1)
        beh2=BehaviorAO.get_behavior(self.eid2)
        beh3=beh1 + beh2
        beh4=beh1 ^ beh2
        beh5=beh1 & beh2
        assert beh3.external_id == ""
        assert beh3.behavior_type=="LUDIC"
        for el in beh4.elements:
            assert beh3.element_count.count(el) ==1
        for el in beh5.elements:
            assert beh3.element_count.count(el) ==2
        assert len(beh3.element_count) == len(beh1)+len(beh2)

    def test_12(self):
        """ Test the mixing of behaviors
        """
        behMec=BehaviorAO.get_behavior(self.eidMech)
        behLud=BehaviorAO.get_behavior(self.eid1)
        bint=behMec & behLud
        bor=behMec | behLud
        bxor=behMec ^ behLud
        bdiff=behMec.difference(behLud)
        assert bint.behavior_type == "composed"
        assert bor.behavior_type == "composed"
        assert bxor.behavior_type == "composed"
        assert bdiff.behavior_type == "composed"
        self.assertRaises(TypeError,behMec.difference_update,behLud)
        
