import sys
import getpass
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

def challenge_code_handler(username, choice):
    print("\n--------------------------------------------------")
    print(f"🔒 Verificación de Seguridad requerida para @{username}")
    if choice == 0:
        print("📩 Se ha enviado un código por SMS a tu número de teléfono.")
    elif choice == 1:
        print("📧 Se ha enviado un código a tu Correo Electrónico registrado.")
    else:
        print("📱 Se requiere un código de verificación de Instagram.")
    print("--------------------------------------------------")
    code = input("Ingresa el código de 6 dígitos que recibiste: ").strip()
    return code

def main():
    print("==================================================")
    print("     Instagram Extractor - Iniciar Sesión        ")
    print("==================================================")
    
    username = input("Ingresa tu nombre de usuario de Instagram: ").strip()
    if not username:
        print("❌ Nombre de usuario no válido.")
        sys.exit(1)

    password = getpass.getpass(prompt=f"Ingresa la contraseña para @{username}: ")
    if not password:
        print("❌ Contraseña requerida.")
        sys.exit(1)

    cl = Client()
    # Asignar manejador de códigos de verificación
    cl.challenge_code_handler = challenge_code_handler
    session_file = Path("session.json")

    try:
        print(f"\nIniciando sesión como @{username}...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"\n✓ ¡Sesión iniciada y guardada con éxito en '{session_file.name}'!")
        print("==================================================")
        print("Ya puedes ejecutar la extracción del perfil deseado:")
        print("  python main.py -u camperomariano")
        print("==================================================\n")

    except TwoFactorRequired:
        print("\n🔒 Tu cuenta tiene habilitada la Autenticación en Dos Pasos (2FA).")
        code = input("Ingresa el código de 6 dígitos de tu aplicación 2FA (Authenticator/SMS): ").strip()
        try:
            cl.login(username, password, verification_code=code)
            cl.dump_settings(session_file)
            print(f"\n✓ ¡Sesión 2FA guardada con éxito en '{session_file.name}'!")
            print("Ya puedes ejecutar: python main.py -u camperomariano")
        except Exception as e:
            print(f"❌ Error al validar código 2FA: {e}")

    except ChallengeRequired:
        print("\n🔒 Instagram requiere aprobación manual del inicio de sesión.")
        print("--------------------------------------------------")
        print("1. Abre la app oficial de Instagram en tu teléfono o instagram.com")
        print("2. Verás un mensaje diciendo '¿Intentaste iniciar sesión?'")
        print("3. Toca en 'FUI YO' / 'THIS WAS ME'")
        print("4. Vuelve a ejecutar inmediatamente: python login.py")
        print("--------------------------------------------------")

    except Exception as e:
        err_msg = str(e)
        if "Manual verification" in err_msg or "checkpoint" in err_msg.lower():
            print("\n🔒 Instagram ha activado un punto de control (Checkpoint).")
            print("--------------------------------------------------")
            print("PASOS PARA APROBAR:")
            print("1. Abre la aplicación de Instagram en tu teléfono móvil.")
            print("2. Aparecerá un aviso en pantalla: '¿Has sido tú?' / 'Intento de inicio de sesión'.")
            print("3. Presiona el botón 'FUI YO' / 'THIS WAS ME'.")
            print("4. Vuelve a ejecutar en la consola: python login.py")
            print("--------------------------------------------------")
        else:
            print(f"\n❌ Error al iniciar sesión: {e}")

if __name__ == "__main__":
    main()
