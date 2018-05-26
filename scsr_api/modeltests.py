import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import unittest

#from admin.models.admin import *
#from sys_app.tests import AppTest
''' 
from scsr.models.test_elements import ElementModelTest
from scsr.models.test_behaviors import BehaviorModelTest
from scsr.models.test_aesthetic_function import AestheticFunctionModelTest
from scsr.models.test_persuasive_function import PersuasiveFunctionModelTest
from scsr.models.test_orchestration_function import OrchestrationFunctionModelTest
from scsr.models.test_reification_function import ReificationFunctionModelTest
from scsr.models.test_scsr import ScsrModelTest '''

#from scsr.models.test_elements import ElementModelTest
from scsr.models.test_behaviors import BehaviorModelTest
#from scsr.models.test_aesthetic_function import AestheticFunctionModelTest
#from scsr.models.test_persuasive_function import PersuasiveFunctionModelTest
#from scsr.models.test_orchestration_function import OrchestrationFunctionModelTest
#from scsr.models.test_reification_function import ReificationFunctionModelTest

#from scsr.models.test_scsr import ScsrModelTest

if __name__ == '__main__':
        unittest.main()