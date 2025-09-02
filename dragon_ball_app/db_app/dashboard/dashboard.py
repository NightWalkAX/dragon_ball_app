# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import frappe


@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard data for Dragon Ball characters"""
    try:
        # Get character statistics
        total_characters = frappe.db.count("Dragon Ball Character")
        
        # Get characters by race
        race_data = frappe.db.sql("""
            SELECT race, COUNT(*) as count
            FROM `tabDragon Ball Character`
            WHERE race IS NOT NULL AND race != ''
            GROUP BY race
            ORDER BY count DESC
        """, as_dict=True)
        
        # Get characters by gender
        gender_data = frappe.db.sql("""
            SELECT gender, COUNT(*) as count
            FROM `tabDragon Ball Character`
            WHERE gender IS NOT NULL AND gender != ''
            GROUP BY gender
            ORDER BY count DESC
        """, as_dict=True)
        
        # Get top characters by Ki
        top_ki_characters = frappe.db.sql("""
            SELECT character_name, ki, max_ki, race, image_url
            FROM `tabDragon Ball Character`
            WHERE ki IS NOT NULL AND ki != ''
            ORDER BY CAST(REPLACE(ki, ',', '') AS UNSIGNED) DESC
            LIMIT 10
        """, as_dict=True)
        
        # Get recent characters
        recent_characters = frappe.db.sql("""
            SELECT character_name, race, gender, creation, image_url
            FROM `tabDragon Ball Character`
            ORDER BY creation DESC
            LIMIT 5
        """, as_dict=True)
        
        return {
            "total_characters": total_characters,
            "race_distribution": race_data,
            "gender_distribution": gender_data,
            "top_ki_characters": top_ki_characters,
            "recent_characters": recent_characters
        }
    except Exception as e:
        frappe.log_error(str(e), "Dashboard Data Error")
        return {
            "error": str(e),
            "total_characters": 0,
            "race_distribution": [],
            "gender_distribution": [],
            "top_ki_characters": [],
            "recent_characters": []
        }


@frappe.whitelist()
def get_character_details(character_name):
    """Get detailed information about a specific character"""
    try:
        frappe.logger().info(f"Searching for character: {character_name}")
        
        # First, find the document name using character_name
        character_doc = frappe.db.get_value(
            "Dragon Ball Character",
            {"character_name": character_name},
            ["name", "character_name"],
            as_dict=True
        )
        
        frappe.logger().info(f"Character doc found: {character_doc}")
        
        if not character_doc:
            frappe.logger().error(f"Dragon Ball Character {character_name} not found")
            return {
                "error": f"Dragon Ball Character {character_name} not found"
            }

        # Get the full document using the actual document name
        character = frappe.get_doc("Dragon Ball Character", character_doc["name"])
        frappe.logger().info(f"Full character document retrieved: {character.name}")

        # Get transformations using the document name (parent field)
        # The table name for child doctypes follows the pattern: tab + DocType name
        transformations = []
        try:
            # Get transformations directly from the document - this is more reliable
            full_doc = frappe.get_doc("Dragon Ball Character", character_doc["name"])
            if hasattr(full_doc, 'transformations') and full_doc.transformations:
                transformations = []
                for t in full_doc.transformations:
                    transformations.append({
                        'transformation_name': t.transformation_name,
                        'ki': t.ki,
                        'image': t.image,
                        'id': t.id
                    })
                frappe.logger().info(f"Got {len(transformations)} transformations from document")
            else:
                frappe.logger().info("No transformations found in document")
        except Exception as doc_error:
            frappe.logger().error(f"Could not get transformations from document: {doc_error}")
            transformations = []
        
        frappe.logger().info(f"Found {len(transformations)} transformations")

        return {
            "character": character.as_dict(),
            "transformations": transformations
        }
    except Exception as e:
        frappe.log_error(str(e), "Character Details Error")
        return {"error": str(e)}


@frappe.whitelist()
def search_characters(search_term=""):
    """Search characters by name or race"""
    try:
        if not search_term:
            return []
        
        characters = frappe.db.sql("""
            SELECT name, character_name, race, gender, ki, image_url
            FROM `tabDragon Ball Character`
            WHERE character_name LIKE %s OR race LIKE %s
            ORDER BY character_name
            LIMIT 20
        """, (f"%{search_term}%", f"%{search_term}%"), as_dict=True)
        
        return characters
    except Exception as e:
        frappe.log_error(str(e), "Character Search Error")
        return []
