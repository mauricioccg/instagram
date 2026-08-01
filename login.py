import sys
import getpass
from pathlib import Path
from instagrapi import Client

def main():
    print("==================================================")
    print("     Instagram Extractor - Iniciar Sesión        ")
    print("==================================================")
    print("Autenticación mediante la API Móvil de Instagram (Evita errores HTTP 429 y 400)\n")
    
    username = input("Ingresa tu nombre de usuario de Instagram: ").strip()
    if not username:
        print("❌ Nombre de usuario no válido.")
        sys.exit(1)

    password = getpass.getpass(prompt=f"Ingresa la contraseña para @{username}: ")
    if not password:
        print("❌ Contraseña requerida.")
        sys.exit(1)

    cl = Client()
    session_file = Path("session.json")

    try:
        print(f"\nIniciando sesión como @{username}...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"\n✓ ¡Sesión iniciada y guardada con éxito en '{session_file.name}'!")
        print("==================================================")
        print("Ahora puedes ejecutar la extracción del perfil deseado:")
        print("  python main.py -u camperomariano")
        print("==================================================\n")
    except Exception as e:
        print(f"\n❌ Error al iniciar sesión: {e}")

if __name__ == "__main__":
    main()
