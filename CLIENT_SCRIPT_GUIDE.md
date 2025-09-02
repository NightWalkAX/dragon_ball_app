# Guía: Client Script para DocType Padre con Child Table

## Problema
¿Cómo hacer que un client script en un DocType padre influya en un DocType hijo (Child Table)?

## Solución
En tu caso, tienes:
- **DocType Padre**: `Dragon Ball Character`
- **DocType Hijo**: `Transformation` (Child Table)

## 1. Configuración de Client Scripts

### Opción 1: Client Script en el archivo DocType (Recomendado)
Archivo: `dragon_ball_character.js`

```javascript
frappe.ui.form.on('Dragon Ball Character', {
    refresh: function(frm) {
        // Botones de sincronización
        add_sync_buttons(frm);
        
        // Actualizar información de transformaciones
        frm.refresh_field('transformations');
    }
});

// Manejador para la Child Table
frappe.ui.form.on('Transformation', {
    transformations_add: function(frm, cdt, cdn) {
        // Cuando se agrega una fila de transformación
        console.log('Nueva transformación agregada');
        frm.refresh_field('transformations');
    },
    
    transformation_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Nombre de transformación cambiado:', row.transformation_name);
    }
});
```

### Opción 2: Client Script Personalizado (Flexible)
Ir a: **Customization > Client Script > New Client Script**

- **DocType**: Dragon Ball Character
- **Script Type**: Form
- **Script**: Usar el código del archivo `dragon_ball_character_custom.js`

## 2. Modificación de la API para Child Tables

### Problema Original
```python
# ❌ Incorrecto - manejo directo de la tabla
def sync_transformations(character_name, transformations_data):
    frappe.db.delete("Transformation", {"parent": character_name})
    for transformation in transformations_data:
        trans_doc = frappe.new_doc("Transformation")
        trans_doc.parent = character_name
        # ...
```

### Solución Correcta
```python
# ✅ Correcto - usando el documento padre
def sync_transformations(character_doc, transformations_data):
    # Limpiar transformaciones existentes
    character_doc.transformations = []
    
    # Agregar nuevas transformaciones
    for transformation in transformations_data:
        transformation_row = character_doc.append("transformations")
        transformation_row.transformation_name = transformation.get('name', '')
        transformation_row.ki = transformation.get('ki', '')
        # ...
```

## 3. Eventos del Client Script para Child Tables

### Eventos Disponibles para Child Tables:
- `{fieldname}_add`: Cuando se agrega una fila
- `{fieldname}_remove`: Cuando se elimina una fila  
- `{fieldname}`: Cuando cambia el valor del campo padre
- `{child_fieldname}`: Cuando cambia un campo específico de la fila

### Ejemplo Completo:
```javascript
frappe.ui.form.on('Dragon Ball Character', {
    refresh: function(frm) {
        // Lógica del documento padre
        update_transformations_display(frm);
    }
});

frappe.ui.form.on('Transformation', {
    // Cuando se agrega una transformación
    transformations_add: function(frm, cdt, cdn) {
        update_transformations_counter(frm);
    },
    
    // Cuando se elimina una transformación  
    transformations_remove: function(frm, cdt, cdn) {
        update_transformations_counter(frm);
    },
    
    // Cuando cambia el nombre de la transformación
    transformation_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        validate_transformation_name(frm, row);
    },
    
    // Cuando cambia el Ki
    ki: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        format_ki_value(row);
        frm.refresh_field('transformations');
    }
});

function update_transformations_counter(frm) {
    let count = frm.doc.transformations ? frm.doc.transformations.length : 0;
    frm.dashboard.clear_comment();
    if (count > 0) {
        frm.dashboard.add_comment(`Este personaje tiene ${count} transformaciones`, 'blue', true);
    }
}
```

## 4. Sincronización Mejorada con Child Tables

```python
def sync_character(character_data):
    try:
        # Crear o actualizar personaje
        if existing_char:
            doc = frappe.get_doc("Dragon Ball Character", existing_char)
        else:
            doc = frappe.new_doc("Dragon Ball Character")
        
        # Actualizar campos del personaje
        doc.character_name = character_data.get('name')
        doc.ki = character_data.get('ki')
        # ...
        
        # ✅ Sincronizar transformaciones ANTES de guardar
        if character_data.get('transformations'):
            sync_transformations(doc, character_data.get('transformations'))
        
        # Guardar el documento (esto guardará tanto padre como hijos)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return doc.name
    except Exception as e:
        frappe.db.rollback()
        raise
```

## 5. Validaciones en el DocType Padre

```python
class DragonBallCharacter(Document):
    def validate(self):
        self.validate_transformations()
    
    def validate_transformations(self):
        if self.transformations:
            transformation_names = []
            for transformation in self.transformations:
                if transformation.transformation_name in transformation_names:
                    frappe.throw(f"Transformación duplicada: {transformation.transformation_name}")
                transformation_names.append(transformation.transformation_name)
    
    def on_update(self):
        # Se ejecuta después de actualizar (incluyendo child tables)
        if self.transformations:
            frappe.logger().info(f"Personaje {self.character_name} actualizado con {len(self.transformations)} transformaciones")
```

## 6. Puntos Clave

1. **Child Tables se manejan través del documento padre**, no directamente
2. **Client Scripts pueden escuchar eventos de Child Tables** usando el nombre del campo
3. **La sincronización debe hacer append/clear en el documento padre**
4. **frm.refresh_field('transformations')** actualiza la tabla en el cliente
5. **locals[cdt][cdn]** accede a la fila específica de la child table

## 7. Debugging

```javascript
// Para debuggear eventos de child tables
frappe.ui.form.on('Transformation', {
    transformations_add: function(frm, cdt, cdn) {
        console.log('Child Table Event - Add');
        console.log('Document:', frm.doc);
        console.log('Child DocType:', cdt);
        console.log('Child Name:', cdn);
        console.log('Row Data:', locals[cdt][cdn]);
    }
});
```

## 8. Resultado Esperado

Con esta configuración:
1. El botón "Sync All Characters" sincroniza todos los personajes y sus transformaciones
2. El botón "Update Character" actualiza un personaje específico
3. Los client scripts muestran información en tiempo real sobre las transformaciones
4. Las validaciones funcionan tanto en el cliente como en el servidor
5. La UI se actualiza automáticamente cuando cambian las transformaciones

¡Tu client script del padre ahora puede influir completamente en el child table!
