import sys
import getpass
from pathlib import Path
from instagrapi import Client

def login_with_cookie():
    print("\n--------------------------------------------------")
    print(" 🔑 INICIO DE SESIÓN MEDIANTE COOKIE 'sessionid'")
    print("--------------------------------------------------")
    print("Pasos para obtener tu 'sessionid':")
    print("1. Abre https://www.instagram.com en tu navegador (Chrome, Edge, Firefox, Brave).")
    print("2. Presiona F12 para abrir las Herramientas de Desarrollador.")
    print("3. Ve a la pestaña 'Aplicación' (Application) o 'Almacenamiento' -> 'Cookies' -> 'https://www.instagram.com'.")
    print("4. Copia el valor de la cookie llamada 'sessionid'.")
    print("--------------------------------------------------")

    session_id = input("\nPega aquí el Valor de tu cookie 'sessionid': ").strip()
    if not session_id:
        print("❌ Cookie no ingresada.")
        return False

    cl = Client()
    try:
        print("\nVerificando cookie sessionid...")
        cl.login_by_sessionid(session_id)
        session_file = Path("session.json")
        cl.dump_settings(session_file)
        print(f"\n✓ ¡Sesión autenticada y guardada con éxito en '{session_file.name}'!")
        print("==================================================")
        print("Ya puedes ejecutar la extracción sin restricciones:")
        print("  python main.py -u camperomariano")
        print("==================================================\n")
        return True
    except Exception as e:
        print(f"❌ Error al validar cookie sessionid: {e}")
        return False

def login_with_credentials():
    print("\n--------------------------------------------------")
    print(" 👤 INICIO DE SESIÓN MEDIANTE USUARIO Y CONTRASEÑA")
    print("--------------------------------------------------")
    username = input("Ingresa tu nombre de usuario de Instagram: ").strip()
    if not username:
        print("❌ Nombre de usuario no válido.")
        return False

    password = getpass.getpass(prompt=f"Ingresa la contraseña para @{username}: ")
    if not password:
        print("❌ Contraseña requerida.")
        return False

    cl = Client()
    session_file = Path("session.json")
    try:
        print(f"\nIniciando sesión como @{username}...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"\n✓ ¡Sesión guardada con éxito en '{session_file.name}'!")
        print("Ya puedes ejecutar: python main.py -u camperomariano\n")
        return True
    except Exception as e:
        print(f"❌ Error al iniciar sesión: {e}")
        return False

def main():
    print("==================================================")
    print("     Instagram Extractor - Iniciar Sesión        ")
    print("==================================================")
    print("Selecciona tu método de autenticación:\n")
    print("1. [RECOMENDADO] Usar cookie 'sessionid' de tu navegador (100% efectivo sin contraseñas ni bloqueos)")
    print("2. Usar usuario y contraseña\n")

    opcion = input("Selecciona una opción (1 o 2): ").strip()
    if opcion == "1":
        login_with_cookie()
    elif opcion == "2":
        login_with_credentials()
    else:
        print("Opción no válida. Ejecutando método por Cookie...")
        login_with_cookie()

if __name__ == "__main__":
    main()
