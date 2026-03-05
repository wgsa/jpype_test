import os
import sys

import jpype


def test_jvm_startup():
    print("Iniciando prueba de JVM en Windows...")
    print(f"Versión de Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")

    classpath_entries = []

    # 1. Intentar localizar org.jpype.jar
    try:
        jpype_base = os.path.dirname(jpype.__file__)
        # Support JAR is usually in site-packages/ (one level above jpype/)
        jpype_jar = os.path.abspath(os.path.join(jpype_base, "..", "org.jpype.jar"))
        if os.path.exists(jpype_jar):
            print(f"Encontrado org.jpype.jar en: {jpype_jar}")
            classpath_entries.insert(0, os.path.normpath(jpype_jar))
        else:
            jpype_jar = os.path.abspath(os.path.join(jpype_base, "org.jpype.jar"))
            if os.path.exists(jpype_jar):
                print(f"Encontrado org.jpype.jar (dentro del folder jpype) en: {jpype_jar}")
                classpath_entries.insert(0, os.path.normpath(jpype_jar))
            else:
                print("ADVERTENCIA: No se encontró org.jpype.jar automáticamente.")
    except Exception as e:
        print(f"Error buscando el JAR: {e}")

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
