import argparse
import sys
from extractor import InstagramExtractor

def main():
    parser = argparse.ArgumentParser(
        description="Extrae publicaciones de Instagram de los últimos 30 días organizadas en carpetas por ID."
    )
    parser.add_argument(
        "-u", "--username",
        type=str,
        help="Nombre del perfil de Instagram a extraer (ej. instagram)"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=30,
        help="Días a extraer hacia atrás desde la fecha actual (por defecto 30 días / 1 mes)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="descargas",
        help="Carpeta de destino (por defecto 'descargas')"
    )
    parser.add_argument(
        "-l", "--login",
        type=str,
        default=None,
        help="Nombre de usuario de Instagram para iniciar sesión (opcional)"
    )

    args = parser.parse_args()

    target_profile = args.username
    if not target_profile:
        print("==================================================")
        print("    Extractor de Publicaciones de Instagram       ")
        print("==================================================")
        target_profile = input("Introduce el usuario de Instagram a extraer: ").strip()

    if not target_profile:
        print("❌ Debes especificar un usuario válido.")
        sys.exit(1)

    extractor = InstagramExtractor(
        output_dir=args.output,
        login_username=args.login
    )

    extractor.extract_recent_posts(
        target_profile=target_profile,
        days=args.days
    )

if __name__ == "__main__":
    main()
