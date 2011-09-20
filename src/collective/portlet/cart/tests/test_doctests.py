import pprint 
import doctest
import interlude
from interlude import interact
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import PloneSite

TESTFILES = [
    '../common.txt',
]

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE
              
class TestCase(FunctionalTestCase):
    
    class layer(PloneSite):
        
        @classmethod
        def setUp(cls):
            import bda.broschuerenshop
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             bda.broschuerenshop)
            fiveconfigure.debug_mode = False
        
        @classmethod
        def tearDown(cls):
            pass              

ZopeTestCase.installProduct('izBroschueren')
setupPloneSite(extension_profiles=['bda.broschuerenshop:default'])

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import FunctionalDocFileSuite as FileSuite
    return unittest.TestSuite([
        FileSuite(
            file, 
            test_class=TestCase,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint,},
        ) for file in TESTFILES
    ])