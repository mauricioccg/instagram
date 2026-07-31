import os
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
            compress_json=False
        )

        if login_username:
            try:
                self.L.load_session_from_file(login_username)
                print(f"✓ Sesión previa cargada correctamente para: {login_username}")
            except Exception:
                print(f"Iniciando sesión interactiva para el usuario: {login_username}")
                self.L.interactive_login(login_username)

    def extract_recent_posts(self, target_profile: str, days: int = 30):
        """
        Extrae las publicaciones de los últimos `days` días del perfil indicado.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"\nBusca de publicaciones de '@{target_profile}' desde {cutoff_date.strftime('%Y-%m-%d')} ({days} días)...")

        try:
            profile = instaloader.Profile.from_username(self.L.context, target_profile)
        except Exception as e:
            print(f"❌ Error al consultar el perfil '{target_profile}': {e}")
            return 0

        posts_processed = 0
        posts_downloaded = 0

        for post in profile.get_posts():
            post_date = post.date_utc.replace(tzinfo=timezone.utc)

            # Verificar si la publicación es anterior al rango de fecha límite
            if post_date < cutoff_date:
                print(f"\nReached date limit ({post_date.strftime('%Y-%m-%d')} < {cutoff_date.strftime('%Y-%m-%d')}). Finalizando extracción.")
                break

            posts_processed += 1
            # Usar el ID numérico único de la publicación (o shortcode) como nombre de carpeta
            post_id = str(post.mediaid)
            post_dir = self.output_dir / post_id
            post_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n[Publicación #{posts_processed}] ID: {post_id} | Fecha: {post_date.strftime('%Y-%m-%d %H:%M')}")

            # 1. Guardar texto/caption en .txt dentro de la carpeta principal del post
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
                # Publicación tipo carrusel (múltiples fotos/vídeos)
                for node in post.get_sidecar_nodes():
                    if node.is_video:
                        media_items.append(('video', node.video_url))
                    else:
                        media_items.append(('foto', node.display_url))
            else:
                # Publicación individual
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

        print(f"\n==========================================")
        print(f"✓ Proceso completado exitosamente.")
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
