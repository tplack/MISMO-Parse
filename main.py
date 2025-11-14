#!/usr/bin/env python3
"""
MISMO XML to JSON Parser
Parses MISMO XML files to JSON format with optional structured loan data extraction.
"""

import xml.etree.ElementTree as ET
import json
import os
import argparse
import sys
from typing import Dict, Any


class MISMOXMLToJSONParser:
    """Parses MISMO XML to JSON format"""
    
    def __init__(self):
        self.namespaces = {
            'mismo': 'http://www.mismo.org/residential/2009/schemas',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
    
    def parse_xml_to_json(self, xml_file_path: str, output_file_path: str) -> None:
        """
        Parse XML file to JSON format
        
        Args:
            xml_file_path: Path to the input XML file
            output_file_path: Path to the output JSON file
        """
        try:
            # Parse XML file
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Parse to dictionary
            json_data = self._element_to_dict(root)
            
            # Write JSON file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully parsed {xml_file_path} to {output_file_path}")
            
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            raise
        except Exception as e:
            print(f"Error parseing XML to JSON: {e}")
            raise
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Parse XML element to dictionary
        
        Args:
            element: XML element to parse
            
        Returns:
            Dictionary representation of the element
        """
        result = {}
        
        # Add text content if present and not empty
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            else:  # Has both text and children
                result['#text'] = element.text.strip()
        
        # Process child elements
        children = {}
        for child in element:
            child_dict = self._element_to_dict(child)
            child_tag = self._clean_tag_name(child.tag)
            
            # Handle multiple children with same tag
            if child_tag in children:
                if not isinstance(children[child_tag], list):
                    children[child_tag] = [children[child_tag]]
                children[child_tag].append(child_dict)
            else:
                children[child_tag] = child_dict
        
        # Merge children into result
        result.update(children)
        
        # If no attributes, text, or children, return empty string
        if not result:
            return ""
        
        return result
    
    def _clean_tag_name(self, tag: str) -> str:
        """
        Clean XML tag name by removing namespace prefixes
        
        Args:
            tag: XML tag name
            
        Returns:
            Cleaned tag name
        """
        # Remove namespace prefix if present
        if '}' in tag:
            return tag.split('}')[1]
        return tag
    
    def _extract_loan_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure loan-specific data from the parseed JSON
        
        Args:
            json_data: The parseed JSON data
            
        Returns:
            Structured loan data
        """
        loan_data = {
            'message_info': {},
            'deal_info': {},
            'collaterals': [],
            'loans': [],
            'parties': [],
            'relationships': []
        }
        
        try:
            # Extract message info
            if 'ABOUT_VERSIONS' in json_data:
                about_versions = json_data['ABOUT_VERSIONS']
                if 'ABOUT_VERSION' in about_versions:
                    about_version = about_versions['ABOUT_VERSION']
                    if isinstance(about_version, list):
                        about_version = about_version[0]
                    loan_data['message_info'] = about_version
            
            # Extract deal info
            if 'DEAL_SETS' in json_data:
                deal_sets = json_data['DEAL_SETS']
                if 'DEAL_SET' in deal_sets:
                    deal_set = deal_sets['DEAL_SET']
                    if isinstance(deal_set, list):
                        deal_set = deal_set[0]
                    
                    if 'DEALS' in deal_set:
                        deals = deal_set['DEALS']
                        if 'DEAL' in deals:
                            deal = deals['DEAL']
                            if isinstance(deal, list):
                                deal = deal[0]
                            loan_data['deal_info'] = deal
                            
                            # Extract collaterals
                            if 'COLLATERALS' in deal:
                                collaterals = deal['COLLATERALS']
                                if 'COLLATERAL' in collaterals:
                                    collateral_list = collaterals['COLLATERAL']
                                    if not isinstance(collateral_list, list):
                                        collateral_list = [collateral_list]
                                    loan_data['collaterals'] = collateral_list
                            
                            # Extract loans
                            if 'LOANS' in deal:
                                loans = deal['LOANS']
                                if 'LOAN' in loans:
                                    loan_list = loans['LOAN']
                                    if not isinstance(loan_list, list):
                                        loan_list = [loan_list]
                                    loan_data['loans'] = loan_list
                            
                            # Extract parties
                            if 'PARTIES' in deal:
                                parties = deal['PARTIES']
                                if 'PARTY' in parties:
                                    party_list = parties['PARTY']
                                    if not isinstance(party_list, list):
                                        party_list = [party_list]
                                    loan_data['parties'] = party_list
            
            # Extract relationships
            if 'RELATIONSHIPS' in json_data:
                relationships = json_data['RELATIONSHIPS']
                if 'RELATIONSHIP' in relationships:
                    relationship_list = relationships['RELATIONSHIP']
                    if not isinstance(relationship_list, list):
                        relationship_list = [relationship_list]
                    loan_data['relationships'] = relationship_list
        
        except Exception as e:
            print(f"Warning: Error extracting structured loan data: {e}")
        
        return loan_data


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Parse MISMO XML files to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input.xml                          # Creates input.json
  %(prog)s input.xml -o output.json          # Custom output file
  %(prog)s input.xml --structured            # Also create structured version
  %(prog)s input.xml -s -o result.json       # Both options combined
        '''
    )
    
    parser.add_argument(
        'input',
        help='Input XML file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: replaces .xml with .json)',
        default=None
    )
    
    parser.add_argument(
        '-s', '--structured',
        action='store_true',
        help='Also create a structured version with extracted loan data'
    )
    
    parser.add_argument(
        '--structured-output',
        help='Custom path for structured output (default: adds _structured suffix)',
        default=None
    )
    
    return parser.parse_args()


def main():
    """Main function to run the parser"""
    args = parse_arguments()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file path
    if args.output:
        json_file = args.output
    else:
        # Replace .xml extension with .json
        base_name = os.path.splitext(args.input)[0]
        json_file = f"{base_name}.json"
    
    # Create parser instance
    parser = MISMOXMLToJSONParser()
    
    try:
        # Parse XML to JSON
        parser.parse_xml_to_json(args.input, json_file)
        
        # Create structured version if requested
        if args.structured:
            if args.structured_output:
                structured_file = args.structured_output
            else:
                base_name = os.path.splitext(json_file)[0]
                structured_file = f"{base_name}_structured.json"
            
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            structured_data = parser._extract_loan_data(json_data)
            
            with open(structured_file, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            
            print(f"Also created structured version: {structured_file}")
        
    except ET.ParseError as e:
        print(f"Error: Invalid XML file - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: Conversion failed - {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
