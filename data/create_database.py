#!/usr/bin/env python3
"""
Creador de base de datos SQLite para el Asistente de Retroalimentación
Ejecuta el esquema SQL y crea la base de datos con todas las tablas, índices y vistas.

Componente: Inicializador de Base de Datos
Requisitos: 11.1 - Datos simulados en cumplimiento de la Ley N.º 29733
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional


def create_database(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> bool:
    """
    Crea la base de datos SQLite ejecutando el esquema SQL.
    
    Args:
        db_path: Ruta donde crear la base de datos. Por defecto: data/asistente_cni.db
        schema_path: Ruta del archivo schema.sql. Por defecto: data/schema.sql
        
    Returns:
        bool: True si la creación fue exitosa, False en caso contrario
        
    Raises:
        sqlite3.Error: Si hay errores en la ejecución del SQL
        FileNotFoundError: Si el archivo schema.sql no existe
    """
    try:
        # Rutas por defecto
        if db_path is None:
            db_path = Path(__file__).parent / "asistente_cni.db"
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.sql"
        
        # Verificar que existe el archivo de esquema
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"No se encontró el archivo de esquema: {schema_path}")
        
        # Leer el esquema SQL
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Conectar a SQLite y ejecutar el esquema
        print(f"Creando base de datos en: {db_path}")
        with sqlite3.connect(db_path) as conn:
            # Habilitar foreign keys y otras configuraciones
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Ejecutar el esquema completo
            conn.executescript(schema_sql)
            
            # Verificar que las tablas se crearon correctamente
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print("Tablas creadas:")
            for table in tables:
                print(f"  - {table}")
            
            # Verificar índices
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            print(f"\nÍndices creados: {len(indexes)}")
            
            # Verificar vistas
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view'
                ORDER BY name
            """)
            views = [row[0] for row in cursor.fetchall()]
            
            print(f"Vistas creadas:")
            for view in views:
                print(f"  - {view}")
            
            print(f"\n✅ Base de datos creada exitosamente: {db_path}")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Error SQLite al crear la base de datos: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Error de archivo: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def verify_database_structure(db_path: Optional[str] = None) -> bool:
    """
    Verifica que la estructura de la base de datos sea correcta.
    
    Args:
        db_path: Ruta de la base de datos a verificar
        
    Returns:
        bool: True si la estructura es correcta, False en caso contrario
    """
    try:
        if db_path is None:
            db_path = Path(__file__).parent / "asistente_cni.db"
            
        if not os.path.exists(db_path):
            print(f"❌ La base de datos no existe: {db_path}")
            return False
            
        # Tablas esperadas según el esquema
        expected_tables = {
            'usuario', 'grupo', 'docente_grupo', 'estudiante_grupo',
            'simulacro', 'simulacro_grupo', 'tema', 'pregunta', 
            'respuesta', 'registro_acceso'
        }
        
        # Vistas esperadas
        expected_views = {
            'estudiantes_activos', 'docentes_grupos', 'simulacros_con_estadisticas'
        }
        
        with sqlite3.connect(db_path) as conn:
            # Verificar tablas
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            actual_tables = {row[0] for row in cursor.fetchall()}
            
            # Verificar vistas
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view'
            """)
            actual_views = {row[0] for row in cursor.fetchall()}
            
            # Comprobar completitud
            missing_tables = expected_tables - actual_tables
            missing_views = expected_views - actual_views
            
            if missing_tables:
                print(f"❌ Tablas faltantes: {missing_tables}")
                return False
                
            if missing_views:
                print(f"❌ Vistas faltantes: {missing_views}")
                return False
            
            # Verificar integridad referencial
            conn.execute("PRAGMA foreign_key_check")
            
            print("✅ Estructura de la base de datos verificada correctamente")
            print(f"   - {len(actual_tables)} tablas")
            print(f"   - {len(actual_views)} vistas")
            
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en verificación: {e}")
        return False


if __name__ == "__main__":
    """Ejecutar directamente para crear la base de datos"""
    import sys
    
    print("🚀 Iniciando creación de base de datos SQLite...")
    print("   Cumplimiento: Ley N.º 29733 - Solo datos simulados")
    print()
    
    # Crear la base de datos
    success = create_database()
    
    if success:
        # Verificar la estructura
        print("\n🔍 Verificando estructura de la base de datos...")
        if verify_database_structure():
            print("\n🎉 ¡Base de datos lista para usar!")
            print("   Siguiente paso: ejecutar seed_simulados.py para datos de prueba")
        else:
            print("\n⚠️  La base de datos se creó pero hay problemas de estructura")
            sys.exit(1)
    else:
        print("\n❌ Error al crear la base de datos")
        sys.exit(1)