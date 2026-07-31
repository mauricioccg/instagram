import os
import time
import requests
import json
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
        self.login_username = login_username
        
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=1
        )

        self.session_loaded = False
        if login_username:
            try:
                self.L.load_session_from_file(login_username)
                print(f"✓ Sesión previa cargada correctamente para: {login_username}")
                self.session_loaded = True
            except Exception:
                print(f"\n🔑 Iniciando autenticación en Instagram para el usuario: '{login_username}'...")
                try:
                    self.L.interactive_login(login_username)
                    self.L.save_session_to_file()
                    print(f"✓ Sesión guardada exitosamente en el equipo.")
                    self.session_loaded = True
                except Exception as e:
                    print(f"❌ Error durante el inicio de sesión: {e}")
        else:
            # Buscar si existe alguna sesión previa guardada localmente
            session_files = list(Path.home().glob(".config/instaloader/session-*")) + \
                            list(Path(os.getenv("LOCALAPPDATA", "")).glob("Instaloader/session-*"))
            if session_files:
                session_username = session_files[0].name.replace("session-", "")
                try:
                    self.L.load_session_from_file(session_username)
                    print(f"✓ Sesión cargada automáticamente para el usuario: {session_username}")
                    self.session_loaded = True
                except Exception:
                    pass

    def extract_recent_posts(self, target_profile: str, days: int = 30):
        """
        Extrae las publicaciones de los últimos `days` días del perfil indicado.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"\nBusca de publicaciones de '@{target_profile}' desde {cutoff_date.strftime('%Y-%m-%d')} ({days} días)...")

        # Método 1: Instaloader
        try:
            profile = instaloader.Profile.from_username(self.L.context, target_profile)
            return self._extract_with_instaloader(profile, cutoff_date, target_profile)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"\n⚠️ Instagram bloqueó la consulta anónima (HTTP 429).")
                if not self.session_loaded:
                    print(f"👉 Solución: Debes autenticarte ejecutando el script con tu usuario de Instagram:")
                    print(f"   python main.py -u {target_profile} -l TU_USUARIO_INSTAGRAM\n")
            else:
                print(f"❌ Error al consultar perfil con Instaloader: {e}")
            
            # Intento de fallback con yt-dlp si está disponible
            return self._extract_with_ytdlp(target_profile, cutoff_date)

    def _extract_with_instaloader(self, profile, cutoff_date, target_profile):
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
                time.sleep(2)

        except Exception as e:
            if "429" in str(e):
                print(f"\n⚠️ Instagram pausó la descarga por límite de peticiones (429).")
                print(f"Se guardaron {posts_downloaded} publicaciones.")
                if not self.session_loaded:
                    print(f"👉 Inicia sesión con: python main.py -u {target_profile} -l TU_USUARIO_INSTAGRAM")
            else:
                print(f"⚠️ Aviso durante descarga: {e}")

        print(f"\n==========================================")
        print(f"✓ Proceso completado.")
        print(f"✓ Publicaciones extraídas: {posts_downloaded}")
        print(f"✓ Guardado en: {self.output_dir.resolve()}")
        print(f"==========================================\n")
        return posts_downloaded

    def _extract_with_ytdlp(self, target_profile: str, cutoff_date: datetime):
        print(f"\nIntentando extracción alternativa para @{target_profile}...")
        try:
            import yt_dlp
        except ImportError:
            print("yt-dlp no está instalado.")
            return 0

        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
        }
        url = f"https://www.instagram.com/{target_profile}/"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info or 'entries' not in info:
                    print("No se encontraron entradas públicas.")
                    return 0

                posts_downloaded = 0
                for entry in info['entries']:
                    if not entry:
                        continue
                    post_id = entry.get('id', '')
                    if not post_id:
                        continue
                    
                    post_dir = self.output_dir / post_id
                    post_dir.mkdir(parents=True, exist_ok=True)

                    caption = entry.get('description', '') or entry.get('title', '')
                    with open(post_dir / "texto.txt", "w", encoding="utf-8") as f:
                        f.write(caption)

                    media_dir = post_dir / "multimedia"
                    media_dir.mkdir(parents=True, exist_ok=True)

                    # Descargar contenido directo
                    post_url = entry.get('url') or f"https://www.instagram.com/p/{post_id}/"
                    ydl_down_opts = {
                        'outtmpl': str(media_dir / '%(title)s_%(id)s.%(ext)s'),
                        'quiet': True
                    }
                    with yt_dlp.YoutubeDL(ydl_down_opts) as ydl_down:
                        ydl_down.download([post_url])
                    posts_downloaded += 1

                return posts_downloaded
        except Exception as e:
            print(f"❌ Extracción alternativa con yt-dlp finalizada: {e}")
            return 0

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
