// Dragon Ball Character Client Script

frappe.ui.form.on('Dragon Ball Character', {
    refresh: function(frm) {
        // Botón para sincronizar todos los personajes
        frm.add_custom_button(__('Sync All Characters'), function() {
            // Show a progress indicator
            frappe.show_alert({
                message: __('Starting character synchronization...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_all_characters',
                callback: function(r) {
                    console.log('Sync all characters response:', r);
                    
                    if (r.message && r.message.status === 'success') {
                        let message = __('Successfully synced {0} characters!', [r.message.synced_count]);
                        
                        // Add error count info if present
                        if (r.message.error_count && r.message.error_count > 0) {
                            message += __(' (Note: {0} characters had errors)', [r.message.error_count]);
                        }
                        
                        if (r.message.total_processed) {
                            message += __(' Total processed: {0}', [r.message.total_processed]);
                        }
                        
                        frappe.msgprint({
                            title: __('Sync Complete'),
                            message: message,
                            indicator: 'green'
                        });
                        
                        // Refresh the current document if it exists
                        if (frm.doc && frm.doc.name) {
                            frm.reload_doc();
                        }
                        
                        // Refresh the transformations table
                        frm.refresh_field('transformations');
                        
                        // Refresh the list view if we're in list mode
                        if (cur_list) {
                            cur_list.refresh();
                        }
                        
                        // Show alert with transformation count after reload
                        setTimeout(function() {
                            if (frm.doc.transformations && frm.doc.transformations.length > 0) {
                                frappe.show_alert({
                                    message: __('Character now has {0} transformations', [frm.doc.transformations.length]),
                                    indicator: 'green'
                                });
                            }
                        }, 1500);
                        
                    } else if (r.exc) {
                        frappe.msgprint({
                            title: __('Sync Error'),
                            message: __('Error syncing characters: {0}', [r.exc]),
                            indicator: 'red'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Sync Warning'),
                            message: __('Sync completed but no clear status received'),
                            indicator: 'orange'
                        });
                    }
                },
                error: function(r) {
                    console.error('Network error during sync:', r);
                    frappe.msgprint({
                        title: __('Network Error'),
                        message: __('Network error while syncing characters. Please check your connection.'),
                        indicator: 'red'
                    });
                }
            });
        });
        
        // Botón para sincronizar personaje individual
        if (frm.doc.api_id) {
            frm.add_custom_button(__('Update Character'), function() {
                frappe.call({
                    method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_single_character',
                    args: {
                        character_id: frm.doc.api_id
                    },
                    callback: function(r) {
                        if (r.message && r.message.status === 'success') {
                            frappe.msgprint(__('Character {0} updated successfully!', [r.message.character]));
                            frm.reload_doc();
                            // Refresh the transformations table
                            frm.refresh_field('transformations');
                            // Show transformations count after update
                            setTimeout(function() {
                                if (frm.doc.transformations && frm.doc.transformations.length > 0) {
                                    frm.dashboard.clear_comment();
                                    frm.dashboard.add_comment(
                                        __('This character has {0} transformations', [frm.doc.transformations.length]), 
                                        'blue', 
                                        true
                                    );
                                }
                            }, 1000);
                        } else if (r.exc) {
                            frappe.msgprint(__('Error updating character: {0}', [r.exc]));
                        }
                    },
                    error: function(r) {
                        frappe.msgprint(__('Network error while updating character'));
                        console.error('Update error:', r);
                    }
                });
            });
        }
        
        // Add debug button in developer mode
        if (frappe.boot.developer_mode) {
            frm.add_custom_button(__('Debug Transformations'), function() {
                if (frm.doc.transformations) {
                    let debug_info = {
                        'Total transformations': frm.doc.transformations.length,
                        'Transformations': []
                    };
                    
                    frm.doc.transformations.forEach(function(trans, index) {
                        debug_info.Transformations.push({
                            'Index': index + 1,
                            'ID': trans.id || 'No ID',
                            'Name': trans.transformation_name || 'No Name',
                            'Ki': trans.ki || 'No Ki',
                            'Image': trans.image ? 'Yes' : 'No'
                        });
                    });
                    
                    console.log('=== TRANSFORMATION DEBUG INFO ===');
                    console.table(debug_info.Transformations);
                    
                    frappe.msgprint({
                        title: __('Debug Info'),
                        message: __('Check browser console for detailed transformation data'),
                        indicator: 'blue'
                    });
                } else {
                    frappe.msgprint(__('No transformations found to debug'));
                }
            }, __('Debug'));
            
            // Add server debug button
            frm.add_custom_button(__('Server Debug'), function() {
                frappe.call({
                    method: 'dragon_ball_app.db_app.api.dragon_ball_api.debug_character_transformations',
                    args: {
                        character_name: frm.doc.name
                    },
                    callback: function(r) {
                        console.log('=== SERVER DEBUG RESPONSE ===');
                        console.log(r.message);
                        
                        if (r.message && r.message.status === 'success') {
                            frappe.msgprint({
                                title: __('Server Debug Complete'),
                                message: __('Character: {0}, Transformations: {1}. Check console for details.', 
                                    [r.message.character_name, r.message.transformations_count]),
                                indicator: 'blue'
                            });
                        } else {
                            frappe.msgprint({
                                title: __('Server Debug Error'),
                                message: r.message ? r.message.message : 'Unknown error',
                                indicator: 'red'
                            });
                        }
                    }
                });
            }, __('Debug'));
            
            // Add test transformation button
            frm.add_custom_button(__('Test Transformation'), function() {
                frappe.call({
                    method: 'dragon_ball_app.db_app.api.dragon_ball_api.test_transformation_creation',
                    callback: function(r) {
                        console.log('=== TEST TRANSFORMATION RESPONSE ===');
                        console.log(r.message);
                        
                        if (r.message && r.message.status === 'success') {
                            frappe.msgprint({
                                title: __('Test Complete'),
                                message: __('Added {0} transformations to {1}', 
                                    [r.message.transformations_added, r.message.character]),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.msgprint({
                                title: __('Test Error'),
                                message: r.message ? r.message.message : 'Unknown error',
                                indicator: 'red'
                            });
                        }
                    }
                });
            }, __('Debug'));
        }
        
        // Mostrar información sobre las transformaciones
        if (frm.doc.transformations && frm.doc.transformations.length > 0) {
            frm.dashboard.add_comment(__('This character has {0} transformations', [frm.doc.transformations.length]), 'blue', true);
        }
    },
    
    // Evento cuando se carga el documento
    onload: function(frm) {
        // Refresh transformations field on load
        if (frm.doc.transformations) {
            frm.refresh_field('transformations');
            console.log('Transformations loaded:', frm.doc.transformations.length);
        }
    },
    
    // Evento cuando el documento termina de cargar completamente
    onload_post_render: function(frm) {
        // Additional check for transformations after render
        if (frm.doc.transformations && frm.doc.transformations.length > 0) {
            console.log('Post render - Found transformations:', frm.doc.transformations.length);
            // Ensure dashboard comment is shown
            setTimeout(function() {
                frm.dashboard.clear_comment();
                frm.dashboard.add_comment(
                    __('This character has {0} transformations', [frm.doc.transformations.length]), 
                    'blue', 
                    true
                );
            }, 500);
        }
    }
});

// Event handler for the transformations child table
frappe.ui.form.on('Transformation', {
    // When a transformation row is added
    transformations_add: function(frm, cdt, cdn) {
        console.log('Transformation row added:', cdn);
    },
    
    // When a transformation row is removed
    transformations_remove: function(frm, cdt, cdn) {
        console.log('Transformation row removed:', cdn);
        // Update the dashboard comment
        let count = frm.doc.transformations ? frm.doc.transformations.length : 0;
        frm.dashboard.clear_comment();
        if (count > 0) {
            frm.dashboard.add_comment(__('This character has {0} transformations', [count]), 'blue', true);
        }
    },
    
    // When transformation data changes
    transformation_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Transformation name changed:', row.transformation_name);
    },
    
    ki: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Transformation Ki changed:', row.ki);
    }
});
