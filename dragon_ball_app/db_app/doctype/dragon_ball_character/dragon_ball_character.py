# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class DragonBallCharacter(Document):
    def validate(self):
        """Validate the character document"""
        self.validate_transformations()
    
    def validate_transformations(self):
        """Validate transformations data"""
        if self.transformations:
            for transformation in self.transformations:
                if not transformation.transformation_name:
                    frappe.throw("Transformation name is required")
                # Additional validation for ki field if needed
                if transformation.ki:
                    try:
                        # Try to clean and validate ki value
                        ki_clean = str(transformation.ki).replace(',', '').strip()
                        if ki_clean and not ki_clean.isdigit():
                            frappe.logger().warning(
                                f"Invalid Ki value for {transformation.transformation_name}: {transformation.ki}"
                            )
                    except Exception as e:
                        frappe.logger().error(f"Error validating Ki: {e}")
    
    def after_insert(self):
        """Called after the document is inserted"""
        frappe.logger().info(f"New character created: {self.character_name}")
        if self.transformations:
            frappe.logger().info(
                f"Character {self.character_name} has "
                f"{len(self.transformations)} transformations"
            )
    
    def on_update(self):
        """Called after the document is updated"""
        frappe.logger().info(f"Character updated: {self.character_name}")
        if self.transformations:
            frappe.logger().info(
                f"Character {self.character_name} now has "
                f"{len(self.transformations)} transformations"
            )
    
    def get_transformations_count(self):
        """Get the number of transformations for this character"""
        return len(self.transformations) if self.transformations else 0
    
    def get_highest_ki_transformation(self):
        """Get the transformation with the highest Ki"""
        if not self.transformations:
            return None
        
        highest_ki_transformation = None
        highest_ki = 0
        
        for transformation in self.transformations:
            if transformation.ki:
                try:
                    ki_value = int(transformation.ki.replace(',', ''))
                    if ki_value > highest_ki:
                        highest_ki = ki_value
                        highest_ki_transformation = transformation
                except (ValueError, AttributeError):
                    continue
        
        return highest_ki_transformation


@frappe.whitelist()
def sync_all_characters():
    """Sync all characters from Dragon Ball API"""
    try:
        frappe.call(
            'dragon_ball_app.db_app.api.dragon_ball_api.sync_all_characters'
        )
        frappe.msgprint("Successfully synced all characters!")
    except Exception as e:
        frappe.throw(f"Error syncing characters: {str(e)}")


@frappe.whitelist()
def sync_single_character(character_id):
    """Sync a single character from Dragon Ball API"""
    try:
        frappe.call(
            'dragon_ball_app.db_app.api.dragon_ball_api.sync_single_character',
            args={'character_id': character_id}
        )
        frappe.msgprint("Character synced successfully!")
    except Exception as e:
        frappe.throw(f"Error syncing character: {str(e)}")
