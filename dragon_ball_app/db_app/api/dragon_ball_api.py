# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import requests
from frappe import _


@frappe.whitelist()
def sync_all_characters():
    """Sync all characters from Dragon Ball API"""
    try:
        # Count existing characters in the database
        existing_count = frappe.db.count("Dragon Ball Character")
        
        # API endpoint for Dragon Ball characters
        api_url = "https://dragonball-api.com/api/characters"
        
        # If we have less than 58 characters, add limit parameter to get all characters
        if existing_count < 58:
            api_url += "?limit=58"

        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            characters = data.get('items', [])
            
            synced_count = 0
            error_count = 0
            
            # Process characters in smaller batches to avoid transaction issues
            batch_size = 5
            for batch_start in range(0, len(characters), batch_size):
                batch_end = min(batch_start + batch_size, len(characters))
                batch = characters[batch_start:batch_end]
                
                batch_num = batch_start//batch_size + 1
                for i, character_summary in enumerate(batch):
                    global_index = batch_start + i
                    character_name = character_summary.get('name', 'Unknown')
                    character_id = character_summary.get('id')
                    
                    try:
                        # Get full character with transformations
                        individual_url = f"https://dragonball-api.com/api/characters/{character_id}"
                        individual_response = requests.get(individual_url, timeout=10)
                        
                        if individual_response.status_code == 200:
                            character_data = individual_response.json()
                            transformations_count = len(character_data.get('transformations', []))
                            print(f"📋 Got full data for {character_name} with {transformations_count} transformations")
                            
                            # Call sync_character_for_mass with complete data
                            result = sync_character_for_mass(character_data)
                        else:
                            print(f"⚠️ Failed to get individual data for {character_name}, using summary data")
                            # Fallback to summary data (without transformations)
                            result = sync_character_for_mass(character_summary)
                        
                        if result:
                            synced_count += 1
                            print(f"✅ Mass sync success: {character_name}")
                        else:
                            error_count += 1
                            print(f"⚠️ Mass sync failed (returned None): {character_name}")
                            
                    except Exception as char_error:
                        error_count += 1
                        print(f"❌ Mass sync error for {character_name}: {str(char_error)}")
                        frappe.log_error(str(char_error), f"Character Mass Sync Error - {character_name}")
                        # Continue with next character instead of failing
                        continue
                
                # Commit batch
                frappe.db.commit()
            
            # Final commit to ensure everything is saved
            frappe.db.commit()
            
            success_message = _("Mass sync completed: {0} successful, {1} errors").format(synced_count, error_count)
            
            frappe.msgprint(success_message)
            
            return {
                "status": "success",
                "synced_count": synced_count,
                "error_count": error_count,
                "total_processed": len(characters)
            }
        else:
            error_msg = f"API request failed with status: {response.status_code}"
            print(f"❌ {error_msg}")
            frappe.throw(_("Failed to fetch characters from API: {0}").format(response.status_code))
    except Exception as e:
        error_msg = f"Critical error in mass sync: {str(e)}"
        frappe.throw(_("Error syncing characters: {0}").format(str(e)))
        frappe.throw(_("Error syncing characters: {0}").format(str(e)))


@frappe.whitelist()
def sync_single_character(character_id):
    """Sync a single character from Dragon Ball API"""
    try:
        api_url = f"https://dragonball-api.com/api/characters/{character_id}"
        
        response = requests.get(api_url)
        if response.status_code == 200:
            character_data = response.json()
            sync_character(character_data)
            
            frappe.msgprint(
                _("Successfully synced character: {0}").format(
                    character_data.get('name', '')
                )
            )
            return {
                "status": "success", 
                "character": character_data.get('name', '')
            }
        else:
            frappe.throw(_("Failed to fetch character from API"))
    except Exception as e:
        frappe.log_error(str(e), "Dragon Ball API Sync Error")
        frappe.throw(_("Error syncing character: {0}").format(str(e)))


def sync_character(character_data):
    """Sync individual character data"""
    character_name = None
    try:
        character_name = character_data.get('name', '').strip()
        api_id = character_data.get('id')
        
        frappe.logger().info(f"=== SYNC CHARACTER START: {character_name} (API ID: {api_id}) ===")
        
        if not character_name:
            frappe.log_error(
                f"Character name is empty for API ID: {api_id}",
                "Character Sync Error"
            )
            return None
        
        # Check if character already exists by API ID first
        existing_char_by_api = frappe.db.exists(
            "Dragon Ball Character", {"api_id": api_id}
        )
        
        # Also check if character exists by name to avoid duplicates
        existing_char_by_name = frappe.db.exists(
            "Dragon Ball Character", {"character_name": character_name}
        )
        
        frappe.logger().info(f"Existing by API ID: {existing_char_by_api}")
        frappe.logger().info(f"Existing by name: {existing_char_by_name}")
        
        if existing_char_by_api:
            # Update existing character by API ID
            doc = frappe.get_doc("Dragon Ball Character", existing_char_by_api)
            frappe.logger().info(f"Updating existing character: {character_name}")
        elif existing_char_by_name:
            # Character with same name exists but different API ID
            frappe.logger().warning(
                f"Character with name '{character_name}' already exists with "
                f"different API ID. Skipping to avoid duplicate names."
            )
            return None
        else:
            # Create new character
            frappe.logger().info(f"Creating new character: {character_name}")
            doc = frappe.new_doc("Dragon Ball Character")
            doc.api_id = api_id
            doc.character_name = character_name
        
        frappe.logger().info("Setting character fields...")
        # Update character fields
        doc.character_name = character_name
        doc.ki = character_data.get('ki', '')
        doc.max_ki = character_data.get('maxKi', '')
        doc.race = character_data.get('race', '')
        doc.gender = character_data.get('gender', '')
        doc.description = character_data.get('description', '')
        doc.image_url = character_data.get('image', '')
        
        frappe.logger().info("About to save document...")
        
        # Save the document FIRST without transformations
        try:
            if doc.is_new():
                frappe.logger().info("Inserting new document...")
                doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.logger().info(f"✓ Document inserted: {doc.name}")
            else:
                frappe.logger().info("Saving existing document...")
                doc.save(ignore_permissions=True)
                frappe.logger().info(f"✓ Document saved: {doc.name}")
        except Exception as save_error:
            frappe.logger().error(f"❌ Error saving document: {save_error}")
            # Try to handle common save errors gracefully
            if "Duplicate entry" in str(save_error):
                frappe.logger().warning("Duplicate entry detected, trying to find existing...")
                existing = frappe.db.exists("Dragon Ball Character", {"character_name": character_name})
                if existing:
                    frappe.logger().info(f"Found existing character: {existing}")
                    doc = frappe.get_doc("Dragon Ball Character", existing)
                else:
                    raise save_error
            else:
                raise save_error
        
        # Now sync transformations AFTER saving
        transformations_data = character_data.get('transformations', [])
        frappe.logger().info(f"Processing {len(transformations_data)} transformations...")
        
        if transformations_data:
            try:
                frappe.logger().info("Calling sync_transformations...")
                success_count = sync_transformations(doc, transformations_data)
                
                frappe.logger().info("Saving with transformations...")
                doc.save(ignore_permissions=True)
                frappe.logger().info(f"✓ Saved with {success_count} transformations")
                
                # Commit each character individually
                frappe.db.commit()
                frappe.logger().info("✓ Database committed")
                
            except Exception as trans_error:
                frappe.logger().error(f"❌ Error with transformations: {trans_error}")
                # Don't let transformation errors kill the character sync
                frappe.log_error(str(trans_error), f"Transformation Error - {character_name}")
                # Still commit the character without transformations
                frappe.db.commit()
                frappe.logger().warning(f"⚠ Character saved without transformations: {character_name}")
        else:
            frappe.logger().info("No transformations to process")
            # Ensure transformations field is initialized even if empty
            doc.set('transformations', [])
            frappe.db.commit()
        
        # Final verification
        doc.reload()
        final_trans_count = len(doc.transformations) if hasattr(doc, 'transformations') and doc.transformations else 0
        frappe.logger().info(f"=== SYNC COMPLETE: {character_name} - {final_trans_count} transformations ===")
        
        return doc.name
        
    except Exception as e:
        error_msg = f"❌ CRITICAL ERROR syncing {character_name or 'Unknown'}: {str(e)}"
        frappe.logger().error(error_msg)
        frappe.log_error(str(e), f"Character Sync Error - {character_name or 'Unknown'}")
        frappe.db.rollback()
        raise


def sync_character_for_mass(character_data):
    """
    Sync individual character data for mass operations
    Similar to sync_character but without individual commits
    """
    character_name = None
    try:
        character_name = character_data.get('name', '').strip()
        api_id = character_data.get('id')
        
        if not character_name:
            frappe.log_error(
                f"Character name is empty for API ID: {api_id}",
                "Character Sync Error"
            )
            return None
        
        # Check if character already exists by API ID first
        existing_char_by_api = frappe.db.exists(
            "Dragon Ball Character", {"api_id": api_id}
        )
        
        # Also check if character exists by name to avoid duplicates
        existing_char_by_name = frappe.db.exists(
            "Dragon Ball Character", {"character_name": character_name}
        )
        
        if existing_char_by_api:
            # Update existing character by API ID
            doc = frappe.get_doc("Dragon Ball Character", existing_char_by_api)
        elif existing_char_by_name:
            # Character with same name exists but different API ID
            return None
        else:
            # Create new character
            doc = frappe.new_doc("Dragon Ball Character")
            doc.api_id = api_id
            doc.character_name = character_name
        # Update character fields
        doc.character_name = character_name
        doc.ki = character_data.get('ki', '')
        doc.max_ki = character_data.get('maxKi', '')
        doc.race = character_data.get('race', '')
        doc.gender = character_data.get('gender', '')
        doc.description = character_data.get('description', '')
        doc.image_url = character_data.get('image', '')

        
        # Save the document FIRST without transformations
        try:
            if doc.is_new():
                frappe.logger().info("Inserting new document...")
                doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.logger().info(f"✓ Document inserted: {doc.name}")
            else:
                frappe.logger().info("Saving existing document...")
                doc.save(ignore_permissions=True)
                frappe.logger().info(f"✓ Document saved: {doc.name}")
        except Exception as save_error:
            frappe.logger().error(f"❌ Error saving document: {save_error}")
            # Try to handle common save errors gracefully
            if "Duplicate entry" in str(save_error):
                frappe.logger().warning(
                    "Duplicate entry detected, trying to find existing..."
                )
                existing = frappe.db.exists(
                    "Dragon Ball Character", 
                    {"character_name": character_name}
                )
                if existing:
                    frappe.logger().info(f"Found existing character: {existing}")
                    doc = frappe.get_doc("Dragon Ball Character", existing)
                else:
                    raise save_error
            else:
                raise save_error
        
        # Now sync transformations AFTER saving - DIRECT APPROACH
        transformations_data = character_data.get('transformations', [])
        
        if transformations_data:
            try:
                print("🔧 Adding transformations directly...")
                
                # Clear existing transformations
                doc.set('transformations', [])
                
                # Add transformations directly (same as debug function)
                successful_count = 0
                for i, transformation in enumerate(transformations_data):
                    try:
                        transformation_name = transformation.get('name', '').strip()
                        transformation_ki = str(transformation.get('ki', ''))
                        transformation_image = transformation.get('image', '')
                        transformation_id = str(transformation.get('id', ''))
                        
                        print(f"  📝 Processing transformation {i+1}: {transformation_name}")
                        
                        if not transformation_name:
                            print(f"⚠️ Skipping transformation {i+1}: empty name")
                            continue
                        
                        transformation_data = {
                            'id': transformation_id,
                            'transformation_name': transformation_name,
                            'image': transformation_image,
                            'ki': transformation_ki
                        }
                        
                        print(f"  🔗 Appending transformation: {transformation_data}")
                        doc.append("transformations", transformation_data)
                        successful_count += 1
                        print(f"  ✅ Added: {transformation_name}")
                        
                    except Exception as trans_error:
                        print(f"❌ Error adding transformation {i+1}: {trans_error}")
                        continue
                
                # Check transformations in memory before save
                in_memory_count = len(doc.transformations) if doc.transformations else 0
                print(f"📊 Transformations in memory before save: {in_memory_count}")
                
                print("💾 Saving with transformations...")
                doc.save(ignore_permissions=True)
                
                # Check transformations after save
                after_save_count = len(doc.transformations) if doc.transformations else 0
                
                # DO NOT commit here - let batch handle commits
                
            except Exception as trans_error:
                # Don't let transformation errors kill the character sync
                frappe.log_error(
                    str(trans_error), 
                    f"Transformation Error - {character_name}"
                )
                # Character will still be saved without transformations
                print(f"⚠️ Character prepared without transformations: {character_name}")
        else:
            # Ensure transformations field is initialized even if empty
            doc.set('transformations', [])
        
        # Final verification (no reload since we haven't committed yet)
        current_trans = doc.transformations if hasattr(doc, 'transformations') else []
        final_trans_count = len(current_trans) if current_trans else 0
        frappe.logger().info(
            f"=== SYNC COMPLETE: {character_name} - "
            f"{final_trans_count} transformations prepared ==="
        )
        
        return doc.name
        
    except Exception as e:
        error_msg = (
            f"❌ CRITICAL ERROR syncing {character_name or 'Unknown'}: "
            f"{str(e)}"
        )
        frappe.logger().error(error_msg)
        frappe.log_error(
            str(e), 
            f"Character Sync Error - {character_name or 'Unknown'}"
        )
        # Don't rollback here - let batch handle rollbacks
        raise


def sync_transformations(character_doc, transformations_data):
    """Sync transformations for a character using append method"""
    character_name = character_doc.character_name
    try:
        frappe.logger().info(f"=== TRANSFORMATION SYNC START: {character_name} ===")
        frappe.logger().info(f"Received {len(transformations_data)} transformations")
        
        # Clear existing transformations properly
        frappe.logger().info("Clearing existing transformations...")
        character_doc.set('transformations', [])
        frappe.logger().info("✓ Cleared existing transformations")
        
        # Add new transformations to the character document
        successful_count = 0
        for i, transformation in enumerate(transformations_data):
            try:
                frappe.logger().info(f"Processing transformation {i+1}/{len(transformations_data)}")
                
                # Create transformation data dict first
                transformation_name = transformation.get('name', '').strip()
                transformation_ki = str(transformation.get('ki', ''))
                transformation_image = transformation.get('image', '')
                transformation_id = str(transformation.get('id', ''))
                
                frappe.logger().info(f"  - Name: '{transformation_name}'")
                frappe.logger().info(f"  - Ki: '{transformation_ki}'")
                frappe.logger().info(f"  - Image: '{transformation_image}'")
                frappe.logger().info(f"  - ID: '{transformation_id}'")
                
                # Skip if transformation name is empty (required field)
                if not transformation_name:
                    frappe.logger().warning(f"❌ Skipping transformation {i+1}: empty name")
                    continue
                
                transformation_data = {
                    'id': transformation_id,
                    'transformation_name': transformation_name,
                    'image': transformation_image,
                    'ki': transformation_ki
                }
                
                # Add the transformation using append
                frappe.logger().info("  - Appending transformation to document...")
                character_doc.append("transformations", transformation_data)
                
                successful_count += 1
                frappe.logger().info(f"  ✓ Successfully added: {transformation_name}")
                
            except Exception as row_error:
                frappe.logger().error(f"  ❌ Error adding transformation {i+1}: {row_error}")
                frappe.log_error(str(row_error), "Transformation Row Error")
                continue
        
        # Verify transformations were added
        current_transformations = character_doc.transformations
        final_count = len(current_transformations) if current_transformations else 0
        frappe.logger().info(f"=== TRANSFORMATION SYNC COMPLETE ===")
        frappe.logger().info(f"Successfully added: {successful_count}/{len(transformations_data)} transformations")
        frappe.logger().info(f"Final count in document: {final_count}")
        
        if final_count == 0 and len(transformations_data) > 0:
            frappe.logger().error("❌ WARNING: No transformations were added despite having data!")
            
        return successful_count
            
    except Exception as e:
        error_msg = f"❌ CRITICAL ERROR in sync_transformations for {character_name}: {e}"
        frappe.logger().error(error_msg)
        frappe.log_error(str(e), f"Transformation Sync Error - {character_name}")
        raise
