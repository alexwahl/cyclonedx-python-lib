import unittest
from unittest import TestCase
from cyclonedx.parser.cyclonedx_fileparser import BomRead

class TestParserLoadJson(TestCase):
    TEST_DATA_FILE = "tests/fixtures/json/1.4/bom_services_simple.json"


    def test_loadjson_metadata_component_name(self):
        loaded_bom=BomRead.bom_from_json_file(self.TEST_DATA_FILE)
        assert(loaded_bom.metadata.component.name=="cyclonedx-python-lib")

if __name__ == '__main__':
    unittest.main()


