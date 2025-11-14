#!/usr/bin/env python3
"""
Unit tests for MISMO XML to JSON Parser
"""

import pytest
import json
import os
import tempfile
import shutil
from main import MISMOXMLToJSONParser


@pytest.fixture
def parser():
    """Create a parser instance for testing"""
    return MISMOXMLToJSONParser()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_xml_simple():
    """Simple XML content for testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <name>Test Name</name>
    <value>123</value>
    <items>
        <item>First</item>
        <item>Second</item>
        <item>Third</item>
    </items>
</root>'''


@pytest.fixture
def sample_xml_with_namespaces():
    """XML with namespaces for testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:mismo="http://www.mismo.org/residential/2009/schemas">
    <mismo:LoanAmount>250000</mismo:LoanAmount>
    <mismo:InterestRate>3.5</mismo:InterestRate>
</root>'''


@pytest.fixture
def sample_xml_with_attributes():
    """XML with attributes for testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <person id="1" type="borrower">
        <name>John Doe</name>
        <age>30</age>
    </person>
</root>'''


@pytest.fixture
def sample_xml_mismo_structure():
    """Sample MISMO-like structure for testing loan data extraction"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<MESSAGE>
    <ABOUT_VERSIONS>
        <ABOUT_VERSION>
            <DataVersionIdentifier>3.4</DataVersionIdentifier>
        </ABOUT_VERSION>
    </ABOUT_VERSIONS>
    <DEAL_SETS>
        <DEAL_SET>
            <DEALS>
                <DEAL>
                    <LOANS>
                        <LOAN>
                            <LoanAmount>250000</LoanAmount>
                            <InterestRate>3.5</InterestRate>
                        </LOAN>
                    </LOANS>
                    <COLLATERALS>
                        <COLLATERAL>
                            <PropertyAddress>123 Main St</PropertyAddress>
                        </COLLATERAL>
                    </COLLATERALS>
                    <PARTIES>
                        <PARTY>
                            <Name>John Doe</Name>
                            <Role>Borrower</Role>
                        </PARTY>
                    </PARTIES>
                </DEAL>
            </DEALS>
        </DEAL_SET>
    </DEAL_SETS>
</MESSAGE>'''


class TestMISMOXMLToJSONParser:
    """Test suite for MISMOXMLToJSONParser class"""
    
    def test_parser_initialization(self, parser):
        """Test that parser initializes with correct namespaces"""
        assert parser is not None
        assert 'mismo' in parser.namespaces
        assert 'xlink' in parser.namespaces
        assert 'xsi' in parser.namespaces
    
    def test_clean_tag_name_with_namespace(self, parser):
        """Test cleaning tag names with namespace prefixes"""
        tag_with_ns = '{http://www.mismo.org/residential/2009/schemas}LoanAmount'
        cleaned = parser._clean_tag_name(tag_with_ns)
        assert cleaned == 'LoanAmount'
    
    def test_clean_tag_name_without_namespace(self, parser):
        """Test cleaning tag names without namespace prefixes"""
        tag_without_ns = 'LoanAmount'
        cleaned = parser._clean_tag_name(tag_without_ns)
        assert cleaned == 'LoanAmount'
    
    def test_parse_simple_xml(self, parser, temp_dir, sample_xml_simple):
        """Test parsing simple XML to JSON"""
        xml_file = os.path.join(temp_dir, 'simple.xml')
        json_file = os.path.join(temp_dir, 'simple.json')
        
        # Write sample XML
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(sample_xml_simple)
        
        # Parse to JSON
        parser.parse_xml_to_json(xml_file, json_file)
        
        # Verify JSON file was created
        assert os.path.exists(json_file)
        
        # Load and verify JSON content
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'name' in data
        assert data['name'] == 'Test Name'
        assert 'value' in data
        assert data['value'] == '123'
        assert 'items' in data
        assert 'item' in data['items']
        assert isinstance(data['items']['item'], list)
        assert len(data['items']['item']) == 3
    
    def test_parse_xml_with_namespaces(self, parser, temp_dir, sample_xml_with_namespaces):
        """Test parsing XML with namespaces"""
        xml_file = os.path.join(temp_dir, 'namespaces.xml')
        json_file = os.path.join(temp_dir, 'namespaces.json')
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(sample_xml_with_namespaces)
        
        parser.parse_xml_to_json(xml_file, json_file)
        
        assert os.path.exists(json_file)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Namespaces should be removed from tag names
        assert 'LoanAmount' in data
        assert 'InterestRate' in data
    
    def test_parse_xml_with_attributes(self, parser, temp_dir, sample_xml_with_attributes):
        """Test parsing XML with attributes"""
        xml_file = os.path.join(temp_dir, 'attributes.xml')
        json_file = os.path.join(temp_dir, 'attributes.json')
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(sample_xml_with_attributes)
        
        parser.parse_xml_to_json(xml_file, json_file)
        
        assert os.path.exists(json_file)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'person' in data
        assert '@attributes' in data['person']
        assert data['person']['@attributes']['id'] == '1'
        assert data['person']['@attributes']['type'] == 'borrower'
        assert data['person']['name'] == 'John Doe'
    
    def test_parse_invalid_xml(self, parser, temp_dir):
        """Test parsing invalid XML raises appropriate error"""
        xml_file = os.path.join(temp_dir, 'invalid.xml')
        json_file = os.path.join(temp_dir, 'invalid.json')
        
        # Write invalid XML
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0"?><root><unclosed>')
        
        # Should raise ParseError
        with pytest.raises(Exception):
            parser.parse_xml_to_json(xml_file, json_file)
    
    def test_parse_nonexistent_file(self, parser, temp_dir):
        """Test parsing non-existent file raises appropriate error"""
        xml_file = os.path.join(temp_dir, 'nonexistent.xml')
        json_file = os.path.join(temp_dir, 'output.json')
        
        with pytest.raises(Exception):
            parser.parse_xml_to_json(xml_file, json_file)
    
    def test_extract_loan_data_structure(self, parser, temp_dir, sample_xml_mismo_structure):
        """Test extracting structured loan data from MISMO XML"""
        xml_file = os.path.join(temp_dir, 'mismo.xml')
        json_file = os.path.join(temp_dir, 'mismo.json')
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(sample_xml_mismo_structure)
        
        parser.parse_xml_to_json(xml_file, json_file)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        structured_data = parser._extract_loan_data(json_data)
        
        # Verify structure
        assert 'message_info' in structured_data
        assert 'deal_info' in structured_data
        assert 'collaterals' in structured_data
        assert 'loans' in structured_data
        assert 'parties' in structured_data
        
        # Verify loans data
        assert len(structured_data['loans']) == 1
        assert structured_data['loans'][0]['LoanAmount'] == '250000'
        
        # Verify collaterals data
        assert len(structured_data['collaterals']) == 1
        assert structured_data['collaterals'][0]['PropertyAddress'] == '123 Main St'
        
        # Verify parties data
        assert len(structured_data['parties']) == 1
        assert structured_data['parties'][0]['Name'] == 'John Doe'
    
    def test_extract_loan_data_with_missing_fields(self, parser):
        """Test extracting loan data when fields are missing"""
        # Empty data
        empty_data = {}
        result = parser._extract_loan_data(empty_data)
        
        assert 'loans' in result
        assert result['loans'] == []
        assert 'collaterals' in result
        assert result['collaterals'] == []
    
    def test_element_to_dict_empty_element(self, parser):
        """Test converting empty XML element to dict"""
        import xml.etree.ElementTree as ET
        element = ET.fromstring('<empty></empty>')
        result = parser._element_to_dict(element)
        assert result == ""
    
    def test_element_to_dict_text_only(self, parser):
        """Test converting text-only element to dict"""
        import xml.etree.ElementTree as ET
        element = ET.fromstring('<text>Some content</text>')
        result = parser._element_to_dict(element)
        assert result == "Some content"
    
    def test_duplicate_child_elements(self, parser, temp_dir):
        """Test handling of duplicate child elements"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item>First</item>
    <item>Second</item>
    <item>Third</item>
</root>'''
        
        xml_file = os.path.join(temp_dir, 'duplicate.xml')
        json_file = os.path.join(temp_dir, 'duplicate.json')
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        parser.parse_xml_to_json(xml_file, json_file)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'item' in data
        assert isinstance(data['item'], list)
        assert len(data['item']) == 3
        assert data['item'][0] == 'First'
        assert data['item'][1] == 'Second'
        assert data['item'][2] == 'Third'


class TestCLIIntegration:
    """Integration tests for command-line interface"""
    
    def test_help_message(self):
        """Test that help message works"""
        import subprocess
        result = subprocess.run(
            ['python', 'main.py', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'MISMO XML' in result.stdout
        assert '--output' in result.stdout
        assert '--structured' in result.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


