# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


def create_sample_characters():
    """Create sample Dragon Ball characters for testing"""
    sample_characters = [
        {
            "character_name": "Goku",
            "ki": "1,000,000",
            "max_ki": "10,000,000",
            "race": "Saiyan",
            "gender": "M",
            "description": "Main protagonist of Dragon Ball series",
            "image_url": "https://dragonball-api.com/characters/goku.jpg"
        },
        {
            "character_name": "Vegeta",
            "ki": "900,000",
            "max_ki": "9,000,000",
            "race": "Saiyan",
            "gender": "M",
            "description": "Prince of the Saiyans",
            "image_url": "https://dragonball-api.com/characters/vegeta.jpg"
        },
        {
            "character_name": "Piccolo",
            "ki": "800,000",
            "max_ki": "5,000,000",
            "race": "Namekian",
            "gender": "M",
            "description": "Former enemy turned ally",
            "image_url": "https://dragonball-api.com/characters/piccolo.jpg"
        },
        {
            "character_name": "Bulma",
            "ki": "5,000",
            "max_ki": "5,000",
            "race": "Human",
            "gender": "F",
            "description": "Brilliant scientist and inventor",
            "image_url": "https://dragonball-api.com/characters/bulma.jpg"
        },
        {
            "character_name": "Frieza",
            "ki": "1,200,000",
            "max_ki": "12,000,000",
            "race": "Frieza Race",
            "gender": "M",
            "description": "Galactic emperor and tyrant",
            "image_url": "https://dragonball-api.com/characters/frieza.jpg"
        }
    ]
    
    created_count = 0
    
    for char_data in sample_characters:
        # Check if character already exists
        existing = frappe.db.exists(
            "Dragon Ball Character", 
            {"character_name": char_data["character_name"]}
        )
        
        if not existing:
            try:
                doc = frappe.new_doc("Dragon Ball Character")
                doc.update(char_data)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
                created_count += 1
                print(f"Created character: {char_data['character_name']}")
            except Exception as e:
                print(f"Error creating {char_data['character_name']}: {str(e)}")
        else:
            print(f"Character already exists: {char_data['character_name']}")
    
    print(f"Sample data creation completed. Created {created_count} characters.")
    return created_count


def create_sample_transformations():
    """Create sample transformations for characters"""
    sample_transformations = [
        {
            "character_name": "Goku",
            "transformations": [
                {
                    "transformation_name": "Super Saiyan",
                    "ki": "2,000,000",
                    "image": "https://dragonball-api.com/transformations/ssj1.jpg"
                },
                {
                    "transformation_name": "Super Saiyan 2",
                    "ki": "4,000,000",
                    "image": "https://dragonball-api.com/transformations/ssj2.jpg"
                },
                {
                    "transformation_name": "Super Saiyan 3",
                    "ki": "8,000,000",
                    "image": "https://dragonball-api.com/transformations/ssj3.jpg"
                }
            ]
        },
        {
            "character_name": "Vegeta",
            "transformations": [
                {
                    "transformation_name": "Super Saiyan",
                    "ki": "1,800,000",
                    "image": "https://dragonball-api.com/transformations/vegeta_ssj1.jpg"
                },
                {
                    "transformation_name": "Super Saiyan 2",
                    "ki": "3,600,000",
                    "image": "https://dragonball-api.com/transformations/vegeta_ssj2.jpg"
                }
            ]
        }
    ]
    
    created_count = 0
    
    for char_data in sample_transformations:
        character = frappe.db.exists(
            "Dragon Ball Character", 
            {"character_name": char_data["character_name"]}
        )
        
        if character:
            try:
                # Clear existing transformations
                frappe.db.delete("Transformation", {"parent": character})
                
                for trans_data in char_data["transformations"]:
                    trans_doc = frappe.new_doc("Transformation")
                    trans_doc.parent = character
                    trans_doc.parenttype = "Dragon Ball Character"
                    trans_doc.parentfield = "transformations"
                    trans_doc.update(trans_data)
                    trans_doc.save(ignore_permissions=True)
                    created_count += 1
                
                frappe.db.commit()
                print(f"Created transformations for: {char_data['character_name']}")
            except Exception as e:
                print(f"Error creating transformations for {char_data['character_name']}: {str(e)}")
        else:
            print(f"Character not found: {char_data['character_name']}")
    
    print(f"Sample transformations created: {created_count}")
    return created_count


@frappe.whitelist()
def setup_sample_data():
    """Setup all sample data"""
    try:
        char_count = create_sample_characters()
        trans_count = create_sample_transformations()
        
        frappe.msgprint(
            f"Sample data setup completed! Created {char_count} characters and {trans_count} transformations."
        )
        
        return {
            "status": "success",
            "characters_created": char_count,
            "transformations_created": trans_count
        }
    except Exception as e:
        frappe.log_error(str(e), "Sample Data Setup Error")
        frappe.throw(f"Error setting up sample data: {str(e)}")


if __name__ == "__main__":
    # For running from command line
    setup_sample_data()
