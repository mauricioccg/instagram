import os
import time
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
import instaloader

class InstagramExtractor:
    """
    Clase para extraer publicaciones de un perfil de Instagram del último mes
    y guardarlas en una estructura de carpetas especificada.
    """
    def __init__(self, output_dir: str = "descargas", login_username: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3
        )

        session_loaded = False
        if login_username:
            try:
                self.L.load_session_from_file(login_username)
                print(f"✓ Sesión previa cargada correctamente para: {login_username}")
                session_loaded = True
            except Exception:
                print(f"⚠️ No se encontró archivo de sesión guardado para '{login_username}'.")
                print(f"Iniciando sesión interactiva para guardar sesión...")
                try:
                    self.L.interactive_login(login_username)
                    self.L.save_session_to_file()
                    print(f"✓ Sesión guardada exitosamente.")
                    session_loaded = True
                except Exception as e:
                    print(f"❌ Error al iniciar sesión: {e}")
        else:
            # Buscar si existe alguna sesión previa guardada localmente
            session_files = list(Path.home().glob(".config/instaloader/session-*")) + \
                            list(Path(os.getenv("LOCALAPPDATA", "")).glob("Instaloader/session-*"))
            if session_files:
                session_username = session_files[0].name.replace("session-", "")
                try:
                    self.L.load_session_from_file(session_username)
                    print(f"✓ Sesión cargada automáticamente para el usuario: {session_username}")
                    session_loaded = True
                except Exception:
                    pass

        if not session_loaded:
            print("ℹ️ Nota: Ejecutando sin sesión iniciada. Si recibes error HTTP 429 (Too Many Requests), ejecuta el script especificando tu usuario con: python main.py -l TU_USUARIO_IG")

    def extract_recent_posts(self, target_profile: str, days: int = 30):
        """
        Extrae las publicaciones de los últimos `days` días del perfil indicado.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"\nBusca de publicaciones de '@{target_profile}' desde {cutoff_date.strftime('%Y-%m-%d')} ({days} días)...")

        try:
            profile = instaloader.Profile.from_username(self.L.context, target_profile)
        except instaloader.exceptions.QueryReturned429Exception:
            print(f"\n❌ Error HTTP 429 (Too Many Requests): Instagram ha limitado las consultas anónimas.")
            print(f"👉 Solución: Inicia sesión ejecutando:\n   python main.py -u {target_profile} -l TU_USUARIO_INSTAGRAM\n")
            return 0
        except Exception as e:
            print(f"❌ Error al consultar el perfil '{target_profile}': {e}")
            return 0

        posts_processed = 0
        posts_downloaded = 0

        try:
            for post in profile.get_posts():
                post_date = post.date_utc.replace(tzinfo=timezone.utc)

                if post_date < cutoff_date:
                    print(f"\nLímite de fecha alcanzado ({post_date.strftime('%Y-%m-%d')} < {cutoff_date.strftime('%Y-%m-%d')}). Finalizando extracción.")
                    break

                posts_processed += 1
                post_id = str(post.mediaid)
                post_dir = self.output_dir / post_id
                post_dir.mkdir(parents=True, exist_ok=True)

                print(f"\n[Publicación #{posts_processed}] ID: {post_id} | Fecha: {post_date.strftime('%Y-%m-%d %H:%M')}")

                # 1. Guardar texto/caption en .txt
                caption_file = post_dir / "texto.txt"
                caption_text = post.caption if post.caption else ""
                with open(caption_file, "w", encoding="utf-8") as f:
                    f.write(caption_text)
                print(f"  └─ 📝 Guardado texto en: {caption_file.name}")

                # 2. Guardar fotos y vídeos en la subcarpeta 'multimedia'
                media_dir = post_dir / "multimedia"
                media_dir.mkdir(parents=True, exist_ok=True)

                media_items = []
                if post.typename == 'GraphSidecar':
                    for node in post.get_sidecar_nodes():
                        if node.is_video:
                            media_items.append(('video', node.video_url))
                        else:
                            media_items.append(('foto', node.display_url))
                else:
                    if post.is_video:
                        media_items.append(('video', post.video_url))
                    else:
                        media_items.append(('foto', post.url))

                for idx, (m_type, url) in enumerate(media_items, start=1):
                    ext = ".mp4" if m_type == 'video' else ".jpg"
                    filename = f"{m_type}_{idx:02d}{ext}"
                    dest_path = media_dir / filename
                    self._download_file(url, dest_path)

                posts_downloaded += 1
                time.sleep(1) # Pausa prudencial entre publicaciones

        except instaloader.exceptions.QueryReturned429Exception:
            print(f"\n⚠️ Instagram bloqueó temporalmente por límite de peticiones (HTTP 429).")
            print(f"Se guardaron {posts_downloaded} publicaciones antes del límite.")
            print(f"👉 Para evitar este límite, inicia sesión ejecutando:\n   python main.py -u {target_profile} -l TU_USUARIO_INSTAGRAM\n")

        print(f"\n==========================================")
        print(f"✓ Proceso completado.")
        print(f"✓ Publicaciones extraídas: {posts_downloaded}")
        print(f"✓ Guardado en: {self.output_dir.resolve()}")
        print(f"==========================================\n")
        return posts_downloaded

    def _download_file(self, url: str, dest_path: Path):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, stream=True, timeout=20)
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"  └─ 📁 Guardado multimedia: multimedia/{dest_path.name}")
        except Exception as e:
            print(f"  └─ ⚠️ Error al descargar multimedia ({dest_path.name}): {e}")

