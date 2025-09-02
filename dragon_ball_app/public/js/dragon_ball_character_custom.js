// Custom Client Script para Dragon Ball Character
// Este script se puede usar como Client Script personalizado en Frappe

frappe.ui.form.on('Dragon Ball Character', {
    refresh: function(frm) {
        // Agregar botones de sincronización
        add_sync_buttons(frm);
        
        // Mostrar información de transformaciones
        show_transformations_info(frm);
        
        // Agregar estilo personalizado
        add_custom_styling(frm);
    },
    
    onload: function(frm) {
        // Configuración inicial cuando se carga el formulario
        setup_transformations_table(frm);
    },
    
    after_save: function(frm) {
        // Acciones después de guardar
        if (frm.doc.transformations && frm.doc.transformations.length > 0) {
            frappe.show_alert({
                message: __('Character saved with {0} transformations', [frm.doc.transformations.length]),
                indicator: 'green'
            }, 3);
        }
    }
});

// Event handlers para la tabla hijo de transformaciones
frappe.ui.form.on('Transformation', {
    transformations_add: function(frm, cdt, cdn) {
        // Cuando se agrega una nueva transformación
        let row = locals[cdt][cdn];
        frappe.show_alert({
            message: __('New transformation row added'),
            indicator: 'blue'
        }, 2);
        
        // Actualizar contador
        update_transformations_counter(frm);
    },
    
    transformations_remove: function(frm, cdt, cdn) {
        // Cuando se elimina una transformación
        frappe.show_alert({
            message: __('Transformation removed'),
            indicator: 'orange'
        }, 2);
        
        // Actualizar contador después de un breve delay
        setTimeout(() => {
            update_transformations_counter(frm);
        }, 100);
    },
    
    transformation_name: function(frm, cdt, cdn) {
        // Cuando cambia el nombre de la transformación
        let row = locals[cdt][cdn];
        if (row.transformation_name) {
            console.log('Transformation name updated:', row.transformation_name);
            
            // Validar que no haya nombres duplicados
            let duplicate = frm.doc.transformations.find(t => 
                t.name !== cdn && t.transformation_name === row.transformation_name
            );
            
            if (duplicate) {
                frappe.msgprint(__('Transformation name already exists: {0}', [row.transformation_name]));
                row.transformation_name = '';
                frm.refresh_field('transformations');
            }
        }
    },
    
    ki: function(frm, cdt, cdn) {
        // Cuando cambia el Ki de la transformación
        let row = locals[cdt][cdn];
        if (row.ki) {
            // Validar formato numérico
            let ki_numeric = row.ki.replace(/,/g, '');
            if (isNaN(ki_numeric)) {
                frappe.msgprint(__('Ki must be a numeric value'));
                row.ki = '';
                frm.refresh_field('transformations');
            } else {
                // Formatear con comas para mejor legibilidad
                row.ki = parseInt(ki_numeric).toLocaleString();
                frm.refresh_field('transformations');
                
                // Mostrar alerta si es un Ki muy alto
                if (parseInt(ki_numeric) > 1000000) {
                    frappe.show_alert({
                        message: __('Wow! That\'s an incredibly high Ki level!'),
                        indicator: 'red'
                    }, 3);
                }
            }
        }
    }
});

// Funciones auxiliares

function add_sync_buttons(frm) {
    // Botón para sincronizar todos los personajes
    frm.add_custom_button(__('Sync All Characters'), function() {
        frappe.confirm(
            __('This will sync all characters from the Dragon Ball API. Continue?'),
            function() {
                frappe.call({
                    method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_all_characters',
                    freeze: true,
                    freeze_message: __('Syncing characters from API...'),
                    callback: function(r) {
                        if (r.message && r.message.status === 'success') {
                            frappe.msgprint({
                                title: __('Success'),
                                message: __('Successfully synced {0} characters!', [r.message.synced_count]),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    }, __('Actions'));
    
    // Botón para sincronizar personaje individual (solo si tiene API ID)
    if (frm.doc.api_id) {
        frm.add_custom_button(__('Update from API'), function() {
            frappe.call({
                method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_single_character',
                args: {
                    character_id: frm.doc.api_id
                },
                freeze: true,
                freeze_message: __('Updating character from API...'),
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Character updated successfully!'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }, __('Actions'));
    }
}

function show_transformations_info(frm) {
    if (frm.doc.transformations && frm.doc.transformations.length > 0) {
        let total_transformations = frm.doc.transformations.length;
        let highest_ki_transformation = get_highest_ki_transformation(frm.doc.transformations);
        
        let message = __('This character has {0} transformations', [total_transformations]);
        
        if (highest_ki_transformation) {
            message += __('<br>Strongest transformation: <strong>{0}</strong> (Ki: {1})', 
                [highest_ki_transformation.transformation_name, highest_ki_transformation.ki]);
        }
        
        frm.dashboard.add_comment(message, 'blue', true);
    }
}

function update_transformations_counter(frm) {
    let count = frm.doc.transformations ? frm.doc.transformations.length : 0;
    
    // Actualizar dashboard
    frm.dashboard.clear_comment();
    if (count > 0) {
        show_transformations_info(frm);
    }
    
    // Actualizar título de la sección
    $('[data-fieldname="transformations"] .section-head .label').text(
        __('Transformations ({0})', [count])
    );
}

function get_highest_ki_transformation(transformations) {
    if (!transformations || transformations.length === 0) return null;
    
    let highest = null;
    let highest_ki = 0;
    
    transformations.forEach(transformation => {
        if (transformation.ki) {
            let ki_numeric = parseInt(transformation.ki.replace(/,/g, ''));
            if (!isNaN(ki_numeric) && ki_numeric > highest_ki) {
                highest_ki = ki_numeric;
                highest = transformation;
            }
        }
    });
    
    return highest;
}

function setup_transformations_table(frm) {
    // Configurar la tabla de transformaciones
    if (frm.fields_dict.transformations) {
        // Personalizar las columnas de la tabla
        frm.fields_dict.transformations.grid.get_field('transformation_name').df.width = '30%';
        frm.fields_dict.transformations.grid.get_field('ki').df.width = '20%';
        frm.fields_dict.transformations.grid.get_field('image').df.width = '30%';
        
        // Agregar validación en tiempo real
        frm.fields_dict.transformations.grid.df.sortable = true;
    }
}

function add_custom_styling(frm) {
    // Agregar estilos CSS personalizados
    if (!$('#dragon_ball_custom_styles').length) {
        $('head').append(`
            <style id="dragon_ball_custom_styles">
                .form-layout .form-page[data-page-name="Dragon Ball Character"] {
                    background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 5px 0;
                }
                
                .form-section[data-fieldname="transformations"] {
                    border: 2px solid #ff6b35;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: #fff9f5;
                }
                
                .form-section[data-fieldname="transformations"] .section-head {
                    background: #ff6b35;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 10px;
                }
            </style>
        `);
    }
}
