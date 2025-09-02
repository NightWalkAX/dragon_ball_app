#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de las transformaciones
en Dragon Ball Character
"""

import sys
import os

# Add the current directory to Python path to import frappe
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_transformation_sync():
    """Test transformation sync functionality"""
    print("🧪 Iniciando pruebas de sincronización de transformaciones...")
    
    # Datos de ejemplo similares a los que vendría de la API
    test_character_data = {
        "id": 999,
        "name": "Test Character",
        "ki": "1000000",
        "maxKi": "2000000", 
        "race": "Test Race",
        "gender": "Male",
        "description": "Character for testing purposes",
        "image": "https://example.com/test.jpg",
        "transformations": [
            {
                "id": 1,
                "name": "Base Form",
                "ki": "1000000",
                "image": "https://example.com/base.jpg"
            },
            {
                "id": 2,
                "name": "Super Form",
                "ki": "5000000", 
                "image": "https://example.com/super.jpg"
            },
            {
                "id": 3,
                "name": "Ultra Form",
                "ki": "10000000",
                "image": "https://example.com/ultra.jpg"
            }
        ]
    }
    
    print(f"📊 Datos de prueba preparados:")
    print(f"   - Personaje: {test_character_data['name']}")
    print(f"   - Transformaciones: {len(test_character_data['transformations'])}")
    
    for i, trans in enumerate(test_character_data['transformations']):
        print(f"     {i+1}. {trans['name']} (Ki: {trans['ki']})")
    
    print("\n✅ Datos de prueba listos para usar con frappe")
    print("🔧 Para usar estos datos:")
    print("   1. Ejecuta 'bench console' en el directorio frappe-bench")
    print("   2. Importa: from dragon_ball_app.db_app.api.dragon_ball_api import sync_character")
    print("   3. Ejecuta: sync_character(test_character_data)")
    print("   donde test_character_data son los datos de arriba")
    
    return test_character_data

def verify_doctype_structure():
    """Verify doctype structure"""
    print("\n🔍 Verificando estructura de DocTypes...")
    
    # Check Dragon Ball Character doctype
    character_doctype_path = "dragon_ball_app/db_app/doctype/dragon_ball_character/dragon_ball_character.json"
    transformation_doctype_path = "dragon_ball_app/db_app/doctype/transformations/transformations.json"
    
    print(f"📁 Verificando archivos:")
    print(f"   - Character DocType: {character_doctype_path}")
    print(f"   - Transformations DocType: {transformation_doctype_path}")
    
    print("\n🔧 Estructura esperada para Transformations:")
    expected_fields = ["id", "name1", "transformation_name", "image", "ki"]
    print("   Campos requeridos:")
    for field in expected_fields:
        print(f"     - {field}")
    
    print("\n⚠️  Nota importante:")
    print("   - transformation_name es campo requerido (required: 1)")
    print("   - istable: 1 indica que es tabla child")
    print("   - El campo 'transformations' en Dragon Ball Character")
    print("     debe tener fieldtype: 'Table' y options: 'Transformation'")

if __name__ == "__main__":
    print("🐉 Dragon Ball App - Test de Transformaciones")
    print("=" * 50)
    
    test_data = test_transformation_sync()
    verify_doctype_structure()
    
    print("\n🚀 Comandos útiles para debugging:")
    print("   bench console")
    print("   frappe.db.sql('SELECT * FROM `tabTransformation`')")
    print("   frappe.db.sql('SELECT name, character_name FROM `tabDragon Ball Character`')")
    print("   doc = frappe.get_doc('Dragon Ball Character', 'character_name')")
    print("   print(len(doc.transformations))")
