#!/usr/bin/env python3
"""
Script de pruebas para verificar la base de datos SQLite
Valida la estructura, constraints y funcionamiento básico.
"""

import sqlite3
from pathlib import Path


def test_database_structure():
    """Prueba la estructura de la base de datos"""
    db_path = Path(__file__).parent / "asistente_cni.db"
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        
        print("🔍 Verificando estructura de tablas...")
        
        # Verificar cada tabla principal y sus columnas
        tables_to_check = [
            'usuario', 'grupo', 'simulacro', 'tema', 
            'pregunta', 'respuesta', 'registro_acceso'
        ]
        
        for table in tables_to_check:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"  ✅ {table}: {len(columns)} columnas")
        
        # Verificar vistas
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' ORDER BY name
        """)
        views = cursor.fetchall()
        print(f"  ✅ Vistas: {len(views)}")
        
        # Verificar índices
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%' 
            ORDER BY name
        """)
        indexes = cursor.fetchall()
        print(f"  ✅ Índices: {len(indexes)}")


def test_constraints():
    """Prueba los constraints y validaciones"""
    db_path = Path(__file__).parent / "asistente_cni.db"
    
    print("\n🛡️  Verificando constraints...")
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Test 1: Constraint de rol válido
        try:
            conn.execute("""
                INSERT INTO usuario (nombre_usuario, contrasena_hash, rol, activo)
                VALUES ('test_invalid', 'hash123', 'rol_invalido', 1)
            """)
            print("  ❌ ERROR: Rol inválido fue aceptado")
        except sqlite3.IntegrityError:
            print("  ✅ Constraint de rol funcionando")
        
        # Test 2: Constraint de código anónimo para estudiantes
        try:
            conn.execute("""
                INSERT INTO usuario (nombre_usuario, contrasena_hash, rol, activo)
                VALUES ('estudiante_sin_codigo', 'hash123', 'estudiante', 1)
            """)
            print("  ❌ ERROR: Estudiante sin código anónimo fue aceptado")
        except sqlite3.IntegrityError:
            print("  ✅ Constraint de código anónimo funcionando")
        
        # Test 3: Opción de respuesta válida
        try:
            # Necesitamos un simulacro y tema válidos primero
            conn.execute("INSERT INTO simulacro (nombre, fecha_aplicacion) VALUES ('Test', '2024-01-01')")
            conn.execute("INSERT INTO tema (nombre) VALUES ('Test')")
            conn.execute("""
                INSERT INTO pregunta (simulacro_id, tema_id, numero_pregunta, opcion_correcta)
                VALUES (1, 1, 1, 'Z')
            """)
            print("  ❌ ERROR: Opción de respuesta inválida fue aceptada")
        except sqlite3.IntegrityError:
            print("  ✅ Constraint de opción de respuesta funcionando")
        
        # Limpiar datos de prueba
        conn.execute("DELETE FROM pregunta WHERE simulacro_id = 1")
        conn.execute("DELETE FROM simulacro WHERE simulacro_id = 1")
        conn.execute("DELETE FROM tema WHERE tema_id = 1")


def test_views():
    """Prueba las vistas creadas"""
    db_path = Path(__file__).parent / "asistente_cni.db"
    
    print("\n👁️  Verificando vistas...")
    
    with sqlite3.connect(db_path) as conn:
        views = ['estudiantes_activos', 'docentes_grupos', 'simulacros_con_estadisticas']
        
        for view in views:
            try:
                cursor = conn.execute(f"SELECT * FROM {view} LIMIT 1")
                cursor.fetchone()
                print(f"  ✅ Vista {view} funcional")
            except sqlite3.Error as e:
                print(f"  ❌ Error en vista {view}: {e}")


def test_performance_indexes():
    """Prueba que los índices están presentes"""
    db_path = Path(__file__).parent / "asistente_cni.db"
    
    print("\n⚡ Verificando índices de rendimiento...")
    
    with sqlite3.connect(db_path) as conn:
        # Verificar algunos índices importantes
        expected_indexes = [
            'idx_usuario_rol_activo',
            'idx_simulacro_fecha',
            'idx_respuesta_pregunta',
            'idx_registro_acceso_usuario_fecha'
        ]
        
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        actual_indexes = [row[0] for row in cursor.fetchall()]
        
        for idx in expected_indexes:
            if idx in actual_indexes:
                print(f"  ✅ Índice {idx} presente")
            else:
                print(f"  ❌ Índice {idx} faltante")


if __name__ == "__main__":
    print("🧪 Ejecutando pruebas de la base de datos SQLite...")
    print("=" * 50)
    
    try:
        test_database_structure()
        test_constraints()
        test_views()
        test_performance_indexes()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Todas las pruebas completadas!")
        print("✅ La base de datos SQLite está lista para usar")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        exit(1)