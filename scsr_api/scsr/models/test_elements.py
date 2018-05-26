import json
import unittest
from mongoengine.connection import _get_db
from scsr.models.elements import ElementAO, ElementDB, ElementReferenceDB, ElementReferenceAO, ElementGameMappingAO, ElementGameMappingDB
from scsr.models.behaviors import BehaviorAO, BehaviorDB
from scsr.models.orchestration_function import OrchestrationFunctionAO, OrchestrationFunctionDB
from application import ScsrAPP
from settings import MONGODB_HOST

"""Class to test the creation and relational mapping of the Element and ElementReference

    The tests consist of:
        Creating an element
        Seeking element
        Seeking and creating element
        Creating an element reference
        Updating an element reference
        Retrieving an element reference

    TODO: Tests of reassignments
"""

class ElementModelTest(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        print("*"*130)
        print(" "*40+"Testing Element Model")
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
        from install_system import start_countries,start_language, start_games, start_genre
        start_countries()
        start_language()
        start_genre()
        start_games()
        ''' start_elements_ontology()
        start_elements_pigd() '''
        #load the elements

    @classmethod
    def tearDownClass(cls):
        db = _get_db()
        db.client.drop_database(db)

    #This test does not deals with APP
    ''' def test_element_class_empty_element(self): '''
    def test_01(self):
        #Create a new element without element data (E1)
        E1=ElementAO()
        ret=E1.save()
        #check
        assert ret is None
        assert E1.external_id is None
        assert len(E1.element.keys()) is 0
        assert E1.reassigned_to is None
        assert len(E1.reassigned_from) is 0
        assert E1.active is True
        assert E1.updated is None
        assert E1.created is None
        #Verify the database
        in_db=ElementDB.objects # pylint: disable=no-member
        assert in_db.count() is 0
        E1=None
    
    ''' def test_element_class_one_data_element(self): '''
    def test_02(self):
        #Create a new element with element data in one language (E2)
        E2=ElementAO()
        E2.add_name("pt","Atirar")
        ret=E2.save()
        #get the persisted element and compare it
        assert ret is not None
        assert E2.external_id is not None
        assert len(E2.element.keys()) is 1
        assert 'pt' in E2.element.keys()
        assert E2.element['pt'] == "Atirar"
        assert E2.reassigned_to is None
        assert not E2.reassigned_from
        assert E2.active is True
        assert E2.updated is not None
        assert E2.created is not None
        #Verify the database
        in_db=ElementDB.objects # pylint: disable=no-member
        assert in_db.count() is 1
        the_el = ElementDB.objects.filter(external_id=E2.external_id).first() # pylint: disable=no-member
        assert len(the_el.element.keys()) is 1
        assert "pt" in the_el.element.keys()
        assert the_el.element["pt"] == "Atirar"
        assert the_el.external_id == E2.external_id
        assert the_el.active is True
        assert the_el.updated is not None
        assert the_el.created is not None
        assert the_el.reassigned_to is None
        assert not the_el.reassigned_from 
        print(E2)
        print("*"*200)
        print(the_el)
        print("*"*200)
        print(E2.__semi_hash__())
        print("*"*200)
        print(the_el.__semi_hash__())
        print("*"*200)
        assert the_el.compare_application(E2)

    ''' def test_element_class_two_data_element(self): '''
    def test_03(self):
        #create element with two names (different lang)
        E3=ElementAO()
        E3.add_name("pt","Pular")
        E3.add_name("en","Jump")
        E3.save()
        #get the persisted element and compare it
        assert E3.external_id is not None
        assert len(E3.element.keys()) is 2
        assert 'pt' in E3.element.keys()
        assert 'en' in E3.element.keys()
        assert E3.element['pt'] is "Pular"
        assert E3.element['en'] is "Jump"
        assert E3.reassigned_to is None
        assert len(E3.reassigned_from) is 0
        assert E3.active is True
        assert E3.updated is not None
        assert E3.created is not None
        #Verify the database
        in_db1=ElementDB.objects # pylint: disable=no-member
        assert in_db1.count() is 2
        the_el1 = ElementDB.objects.filter(external_id=E3.external_id).first() # pylint: disable=no-member
        assert len(the_el1.element.keys()) is 2
        assert "pt" in the_el1.element.keys()
        assert "en" in the_el1.element.keys()
        assert the_el1.element["pt"] == "Pular"
        assert the_el1.element["en"] == "Jump"
        assert the_el1.external_id == E3.external_id
        assert the_el1.active is True
        assert the_el1.updated is not None
        assert the_el1.created is not None
        assert the_el1.reassigned_to is None
        assert not the_el1.reassigned_from 
        assert the_el1.compare_application(E3)

        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,E3.add_name,"ru","Begat")
        the_el8 = ElementDB.objects.filter(external_id=E3.external_id).first() # pylint: disable=no-member
        assert len(the_el8.element.keys()) is 2

    ''' def test_element_class_seek_element(self): '''
    def test_04(self):
        #seek_or_create element (creating) (E4)
        E4=ElementAO.seek_or_create("pt","Andar")
        ######################
        assert E4.external_id is not None
        assert len(E4.element.keys()) is 1
        assert 'pt' in E4.element.keys()
        assert E4.element['pt'] == "Andar"
        assert E4.reassigned_to is None
        assert not E4.reassigned_from
        assert E4.active is True
        assert E4.updated is not None
        assert E4.created is not None
        #Verify the database We must have only 3 data
        in_db2=ElementDB.objects # pylint: disable=no-member
        assert in_db2.count() is 3
        the_el = ElementDB.objects.filter(external_id=E4.external_id).first() # pylint: disable=no-member
        assert len(the_el.element.keys()) is 1
        assert "pt" in the_el.element.keys()
        assert the_el.element["pt"] == "Andar"
        assert the_el.external_id == E4.external_id
        assert the_el.active is True
        assert the_el.updated is not None
        assert the_el.created is not None
        assert the_el.reassigned_to is None
        assert not the_el.reassigned_from 
        assert the_el.compare_application(E4)



        #seek_or_create element (seeking)

        E5=ElementAO.seek_or_create("pt","Andar")

        assert E5.external_id == E4.external_id

        in_db3=ElementDB.objects # pylint: disable=no-member
        assert in_db3.count() is 3
        #get persisted from sought and compare it
        the_els=ElementDB.objects( __raw__={"element.pt":"Andar"}) # pylint: disable=no-member
        assert the_els.count() is 1
        the_el5=the_els[0]
        assert len(the_el5.element.keys()) is 1
        assert "pt" in the_el5.element.keys()
        assert the_el5.element["pt"] == "Andar"
        assert the_el5.external_id == E5.external_id
        assert the_el5.active is True
        assert the_el5.updated is not None
        assert the_el5.created is not None
        assert the_el5.reassigned_to is None
        assert not the_el5.reassigned_from 
        assert the_el5.compare_application(E5)

    ''' def test_element_class_check_reference(self): '''
    def test_05(self):
        """Data were created, the elements must have been too.
        """

        #each created element generates a reference data.
        #check reference data for E2
        E2=ElementAO.seek_or_create("pt","Atirar")
        in_db3=ElementDB.objects # pylint: disable=no-member
        assert in_db3.count() is 3

        #check reference data for E3
        E3=ElementAO.seek_or_create("pt","Pular")
        in_db3=ElementDB.objects # pylint: disable=no-member
        assert in_db3.count() is 3

        #check reference data for E4
        E4=ElementAO.seek_or_create("pt","Andar")
        in_db3=ElementDB.objects # pylint: disable=no-member
        assert in_db3.count() is 3

        R2=ElementReferenceAO.get_reference(E2)
        assert R2.reference["type"] == 'single'
        assert R2.reference["source"] == 'text'
        assert R2.reference["ref"] == "No Reference"

        R3=ElementReferenceAO.get_reference(E3)
        assert R3.reference["type"] == 'single'
        assert R3.reference["source"] == 'text'
        assert R3.reference["ref"] == "No Reference"

        R4=ElementReferenceAO.get_reference(E4)
        assert R4.reference["type"] == 'single'
        assert R4.reference["source"] == 'text'
        assert R4.reference["ref"] == "No Reference"

        #update ref
        R2.set_reference({"type":"single","source":"link","ref":"www.gamegesis.com"})
        R2.save()

        Rdb2=ElementReferenceDB.objects.filter(element=ElementDB.objects.filter(external_id=R2.element.external_id).first()).first() # pylint: disable=no-member
        assert Rdb2.reference["type"]==R2.reference["type"]
        assert Rdb2.reference["source"]==R2.reference["source"]
        assert Rdb2.reference["ref"]==R2.reference["ref"]

        #update ref
        R3.set_reference({"type":"multi","source":"link","ref":["www.gamegesis.com", "www.hiperlogic.com.br"]})
        R3.save()

        Rdb3=ElementReferenceDB.objects.filter(element=ElementDB.objects.filter(external_id=R3.element.external_id).first()).first() # pylint: disable=no-member
        assert Rdb3.reference["type"]==R3.reference["type"]
        assert Rdb3.reference["source"]==R3.reference["source"]
        assert len(Rdb3.reference["ref"])==len(R3.reference["ref"])
        for txt in Rdb3.reference["ref"]:
            assert txt in R3.reference["ref"]

        #update ref
        # Wrong ref data
        #trying to assign a name in a language not supported by the system
        self.assertRaises(RuntimeError,R4.set_reference,{"type":"single","source":"multi","ref":[{"type":"single", "source":"text", "ref":"txt1"},{"type":"multi", "source":"link", "ref":["link1","link2"]}]})


        R4.set_reference({"type":"multi","source":"multi","ref":[{"type":"single", "source":"text", "ref":"txt1"},{"type":"multi", "source":"link", "ref":["link1","link2"]}]})
        R4.save()
        Rdb4=ElementReferenceDB.objects.filter(element=ElementDB.objects.filter(external_id=R4.element.external_id).first()).first() # pylint: disable=no-member
        assert Rdb4.reference["type"]==R4.reference["type"]
        assert Rdb4.reference["source"]==R4.reference["source"]
        assert len(Rdb4.reference["ref"])==len(R4.reference["ref"])
        for txt in Rdb4.reference["ref"]:
            assert txt in R4.reference["ref"]



    ''' def test_element_class_delete_element(self): '''
    def test_06(self):
        #seek element E4 and delete it (via AO)
        E4=ElementAO.seek_or_create("pt","Andar")
        in_db3=ElementDB.objects # pylint: disable=no-member
        assert in_db3.count() is 3
        assert E4.element["pt"]=="Andar"
        E4.delete()
        assert E4.active is False
        the_el = ElementDB.objects.filter(external_id=E4.external_id).first() # pylint: disable=no-member
        assert the_el.active is False
        
    ''' def test_element_class_reassign_element(self): '''
    def test_07(self):
        # TODO: This one is responsibility of the admin Class.
        #seek element to deprecate (E3)
        #create element to deprecate (E5)
        #seek element to assign to (E2)
        #assign E3, E5 to E2
        #check deprecated elements (reassigned_to and active)
        #check reassigned element (reassigned_from)
        #create element to assign to deprecated
        #assign
        #the assigned_to must be the end of the chain, not the deprecated.
        pass

    

    