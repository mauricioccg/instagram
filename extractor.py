import os
import time
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from instagrapi import Client

class InstagramExtractor:
    """
    Clase para extraer publicaciones de un perfil de Instagram del último mes
    utilizando la API Privada Móvil de Instagram (instagrapi).
    """
    def __init__(self, output_dir: str = "descargas", login_username: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cl = Client()
        self.session_file = Path("session.json")

        self.session_loaded = False
        if self.session_file.exists():
            try:
                self.cl.load_settings(self.session_file)
                print(f"✓ Sesión activa cargada desde '{self.session_file.name}'")
                self.session_loaded = True
            except Exception as e:
                print(f"⚠️ Archivo de sesión '{self.session_file.name}' dañado: {e}")

        if login_username and not self.session_loaded:
            import getpass
            print(f"\n🔑 Autenticando en Instagram como @{login_username}...")
            password = getpass.getpass(prompt=f"Introduce la contraseña para @{login_username}: ")
            try:
                self.cl.login(login_username, password)
                self.cl.dump_settings(self.session_file)
                print(f"✓ Sesión guardada exitosamente en '{self.session_file.name}'")
                self.session_loaded = True
            except Exception as e:
                print(f"❌ Error al iniciar sesión: {e}")

    def extract_recent_posts(self, target_profile: str, days: int = 30):
        """
        Extrae las publicaciones de los últimos `days` días del perfil indicado.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"\nBusca de publicaciones de '@{target_profile}' desde {cutoff_date.strftime('%Y-%m-%d')} ({days} días)...")

        try:
            if not self.session_loaded:
                print("ℹ️ Consulta realizada sin sesión previa en session.json.")
            
            user_id = self.cl.user_id_from_username(target_profile)
            print(f"✓ ID de usuario recuperado: {user_id}")
        except Exception as e:
            print(f"\n❌ No se pudo consultar la cuenta '@{target_profile}': {e}")
            print(f"👉 Solución recomendada: Inicia sesión primero ejecutando:")
            print(f"   python login.py\n")
            return 0

        posts_processed = 0
        posts_downloaded = 0

        try:
            # Consultar lista de publicaciones usando la API móvil (resistente a errores web 400 / 429)
            medias = self.cl.user_medias(user_id, amount=50)

            for media in medias:
                taken_at = media.taken_at
                if taken_at.tzinfo is None:
                    taken_at = taken_at.replace(tzinfo=timezone.utc)

                if taken_at < cutoff_date:
                    print(f"\nLímite de fecha alcanzado ({taken_at.strftime('%Y-%m-%d')} < {cutoff_date.strftime('%Y-%m-%d')}). Finalizando extracción.")
                    break

                posts_processed += 1
                post_id = str(media.pk)
                post_dir = self.output_dir / post_id
                post_dir.mkdir(parents=True, exist_ok=True)

                print(f"\n[Publicación #{posts_processed}] ID: {post_id} | Fecha: {taken_at.strftime('%Y-%m-%d %H:%M')}")

                # 1. Guardar el texto/caption en 'texto.txt'
                caption_file = post_dir / "texto.txt"
                caption_text = media.caption_text if media.caption_text else ""
                with open(caption_file, "w", encoding="utf-8") as f:
                    f.write(caption_text)
                print(f"  └─ 📝 Guardado texto en: {caption_file.name}")

                # 2. Guardar las fotos y vídeos en la subcarpeta 'multimedia'
                media_dir = post_dir / "multimedia"
                media_dir.mkdir(parents=True, exist_ok=True)

                media_items = []
                if media.media_type == 8 and media.resources:
                    # Carrusel
                    for res in media.resources:
                        if res.media_type == 2 and res.video_url:
                            media_items.append(('video', str(res.video_url)))
                        elif res.thumbnail_url:
                            media_items.append(('foto', str(res.thumbnail_url)))
                elif media.media_type == 2 and media.video_url:
                    # Vídeo individual
                    media_items.append(('video', str(media.video_url)))
                elif media.thumbnail_url:
                    # Foto individual
                    media_items.append(('foto', str(media.thumbnail_url)))

                for idx, (m_type, url) in enumerate(media_items, start=1):
                    ext = ".mp4" if m_type == 'video' else ".jpg"
                    filename = f"{m_type}_{idx:02d}{ext}"
                    dest_path = media_dir / filename
                    self._download_file(url, dest_path)

                posts_downloaded += 1
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Ocurrió una excepción durante la descarga: {e}")

        print(f"\n==========================================")
        print(f"✓ Proceso completado.")
        print(f"✓ Publicaciones extraídas: {posts_downloaded}")
        print(f"✓ Guardado en: {self.output_dir.resolve()}")
        print(f"==========================================\n")
        return posts_downloaded

    def _download_file(self, url: str, dest_path: Path):
        try:
            headers = {
                'User-Agent': 'Instagram 275.0.0.27.98 Android'
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
