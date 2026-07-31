import sys
import instaloader

def main():
    print("==================================================")
    print("     Instagram Extractor - Iniciar Sesión        ")
    print("==================================================")
    print("Para evitar el error HTTP 429 de Instagram, debes iniciar sesión una sola vez.\n")
    
    username = input("Ingresa tu nombre de usuario de Instagram: ").strip()
    if not username:
        print("❌ Nombre de usuario no válido.")
        sys.exit(1)

    L = instaloader.Instaloader()
    try:
        print(f"\nAutenticando a @{username} en Instagram...")
        L.interactive_login(username)
        L.save_session_to_file()
        print(f"\n✓ ¡Sesión guardada con éxito en tu equipo para '{username}'!")
        print("==================================================")
        print("Ya puedes ejecutar la extracción del perfil sin bloqueos 429:")
        print("  python main.py -u camperomariano")
        print("==================================================\n")
    except Exception as e:
        print(f"\n❌ Error al iniciar sesión: {e}")

if __name__ == "__main__":
    main()
