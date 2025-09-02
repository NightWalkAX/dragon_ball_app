# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from dragon_ball_app.db_app.api.dragon_ball_api import sync_character


def test_basic_character_creation():
    """Simple test for character creation"""
    print("=== BASIC CHARACTER CREATION TEST ===")
    
    # Test data
    test_data = {
        "id": 999,
        "name": "Test Goku",
        "ki": "60.000.000",
        "maxKi": "90 Septillion",
        "race": "Saiyan",
        "gender": "Male",
        "description": "Test character",
        "image": "https://example.com/goku.jpg",
        "transformations": [
            {
                "id": 1,
                "name": "Test Transformation",
                "image": "https://example.com/trans.jpg",
                "ki": "6.000.000"
            }
        ]
    }
    
    try:
        # Clean up any existing test data
        existing_chars = frappe.get_all("Dragon Ball Character", 
                                       filters={"character_name": "Test Goku"})
        for char in existing_chars:
            frappe.delete_doc("Dragon Ball Character", char.name, 
                             ignore_permissions=True)
        frappe.db.commit()
        
        print("✓ Cleaned up existing test data")
        
        # Test character creation
        result = sync_character(test_data)
        
        if result:
            print(f"✓ Character created successfully: {result}")
            
            # Verify the character
            doc = frappe.get_doc("Dragon Ball Character", result)
            print(f"✓ Character name: {doc.character_name}")
            print(f"✓ API ID: {doc.api_id}")
            print(f"✓ Race: {doc.race}")
            print(f"✓ Gender: {doc.gender}")
            
            # Check transformations
            trans_count = len(doc.transformations) if doc.transformations else 0
            print(f"✓ Transformations: {trans_count}")
            
            if trans_count > 0:
                for i, trans in enumerate(doc.transformations):
                    print(f"  - {i+1}: {trans.transformation_name} (Ki: {trans.ki})")
            
            # Clean up
            frappe.delete_doc("Dragon Ball Character", result, 
                             ignore_permissions=True)
            frappe.db.commit()
            print("✓ Test data cleaned up")
            
            return True
        else:
            print("✗ Character creation failed")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


@frappe.whitelist()
def run_basic_test():
    """Run basic test from Frappe interface"""
    result = test_basic_character_creation()
    if result:
        frappe.msgprint("Basic test passed!")
    else:
        frappe.msgprint("Basic test failed!")
    return result


if __name__ == "__main__":
    test_basic_character_creation()
