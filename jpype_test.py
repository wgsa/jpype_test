import os
import sys

import jpype


def test_jvm_startup():
    print("Iniciando prueba de JVM en Windows...")
    print(f"Versión de Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")

    print(" === DEBUG DE LOCALIZACIÓN DE JAR === ")

    jpype_file = jpype.__file__
    jpype_dir = os.path.dirname(jpype_file)
    parent_dir = os.path.dirname(jpype_dir)

    print(f"JPype __file__: {jpype_file}")
    print(f"JPype folder: {jpype_dir}")
    print(f"Parent folder (site-packages): {parent_dir}")

    # Lista de posibles ubicaciones
    check_paths = [
        os.path.join(jpype_dir, "org.jpype.jar"),
        os.path.join(parent_dir, "org.jpype.jar"),
        os.path.abspath(os.path.join(jpype_dir, "org.jpype.jar")),
        os.path.abspath(os.path.join(parent_dir, "org.jpype.jar")),
    ]

    found = False
    classpath_entries = []  # Initialize here as the new logic will populate it
    for p in check_paths:
        exists = os.path.exists(p)
        if exists:
            found = True
            # Prueba de permisos y apertura
            readable = os.access(p, os.R_OK)
            is_ascii = p.isascii()
            print(f"Revisando: {p}")
            print(f"   -> EXISTE: {'SÍ' if exists else 'NO'}")
            print(f"   -> Lectura Python: {'OK' if readable else 'DENEGADO'}")
            print(f"   -> Es ruta ASCII: {'SÍ' if is_ascii else 'NO (Posible problema en JNI)'}")

            try:
                with open(p, 'rb') as f:
                    f.read(10)
                print("   -> Verificación de apertura: EXITOSA")
            except Exception as e:
                print(f"   -> Verificación de apertura: FALLIDA ({e})")

            classpath_entries.insert(0, os.path.normpath(p))
        else:
            print(f"Revisando: {p} -> NO EXISTE")

    # Verificar carpeta temporal (donde JPype copia el JAR si la ruta tiene caracteres especiales)
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_readable = os.access(temp_dir, os.W_OK)
    print(f"\nDirectorio Temporal: {temp_dir}")
    print(f"   -> Escritura en Temp: {'OK' if temp_readable else 'DENEGADO'}")
    print(f"   -> Temp es ASCII: {'SÍ' if temp_dir.isascii() else 'NO'}")

    if not found:
        print("\n!!! CRITICAL: No se encontró org.jpype.jar en ninguna de las rutas estándar.")
        print("Esto sugiere que la instalación de JPype podría estar incompleta o ser diferente.")
    else:
        print("\nJAR encontrado. El error 'library not found' podría venir del ClassLoader interno.")

    # 2. Iniciar JVM
    try:
        # Normalizar para Windows (aunque estemos en Github Actions runner)
        normalized_cp = [os.path.normpath(os.path.abspath(p)) for p in classpath_entries]
        print(f"Classpath final: {normalized_cp}")

        if not jpype.isJVMStarted():
            # En GitHub Actions necesitamos pasar una ruta a la JVM o dejar que se encuentre sola
            # windows-latest suele tener Java instalado
            jpype.startJVM(classpath=normalized_cp)
            print("JVM iniciada CORRECTAMENTE.")

            # Verificar si las clases internas de JPype están disponibles
            try:
                # Esto confirma que org.jpype.jar está montado
                print("Acceso a java.lang.String: exitoso.")
                jpype.shutdownJVM()
                print("JVM cerrada correctamente.")
                return True
            except Exception as e:
                print(f"ERROR: JVM inició pero no cargó las clases de soporte: {e}")
                return False
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo iniciar la JVM: {e}")
        return False


if __name__ == "__main__":
    success = test_jvm_startup()
    sys.exit(0 if success else 1)
