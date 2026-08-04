# Instagram Feed Extractor (Último Mes)

Aplicación en Python que extrae publicaciones de un perfil de Instagram del último mes (30 días por defecto) y las organiza automáticamente en la estructura de carpetas especificada.

## 📁 Estructura de Salida

Cada publicación del último mes se guarda en la carpeta de descargas con la siguiente estructura:

```text
descargas/
 └── [NOMBRE_PERFIL]/
      └── [ID_PUBLICACION]/
           ├── texto.txt             # Texto / Descripción (caption) de la publicación
           ├── foto_01.jpg           # Fotos pertenecientes a la publicación
           ├── video_01.mp4          # Vídeos pertenecientes a la publicación
           └── ...
```

## 🚀 Requisitos e Instalación

Asegúrate de tener Python 3.8+ instalado. Luego, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## 💻 Uso

### 1. Modo Interactivo
Ejecuta el script y sigue las instrucciones en pantalla:
```bash
python main.py
```

### 2. Modo Línea de Comandos (CLI)
Puedes especificar el perfil de Instagram y opciones adicionales directamente:
```bash
python main.py -u instagram -d 30 -o descargas
```

### Opciones Disponibles:
- `-u`, `--username`: Nombre de usuario del perfil a extraer (ej. `instagram`).
- `-d`, `--days`: Rango de días hacia atrás (por defecto `30` días).
- `-o`, `--output`: Nombre del directorio de salida (por defecto `descargas`).
- `-l`, `--login`: Usuario de Instagram para iniciar sesión opcional (útil para perfiles restringidos o sesiones privadas).
