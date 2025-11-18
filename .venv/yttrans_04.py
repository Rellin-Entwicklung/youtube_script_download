from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter
import textwrap
import re
from urllib.parse import urlparse, parse_qs
import yt_dlp
import os


def extract_video_id(url_or_id):
    """
    Extrahiert die Video-ID aus einer YouTube-URL oder gibt die ID direkt zurück.
    Unterstützt verschiedene YouTube-URL-Formate.
    """
    # Wenn es bereits eine reine Video-ID ist (11 Zeichen)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    # Parse verschiedene YouTube-URL-Formate
    patterns = [
        r'(?:v=|/)([a-zA-Z0-9_-]{11})',  # Standard und Short URLs
        r'(?:embed/)([a-zA-Z0-9_-]{11})',  # Embed URLs
        r'(?:watch\?v=)([a-zA-Z0-9_-]{11})',  # Watch URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Versuche mit urlparse als Fallback
    try:
        parsed_url = urlparse(url_or_id)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
    except:
        pass

    raise ValueError(f"Konnte keine gültige Video-ID aus '{url_or_id}' extrahieren")


def get_video_info(video_id):
    """
    Holt Informationen über das Video, inkl. Titel.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('title', f"youtube_{video_id}")
    except:
        return f"youtube_{video_id}"


def sanitize_filename(filename):
    """
    Entfernt ungültige Zeichen aus Dateinamen.
    """
    # Ersetze ungültige Zeichen
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Begrenze Länge
    return filename[:200]


def download_audio(video_id, output_filename):
    """
    Lädt das Audio des Videos als MP3 herunter.
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_filename,
            'quiet': False,
            'no_warnings': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Lade Audio herunter...")
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        return True
    except Exception as e:
        print(f"Fehler beim Audio-Download: {e}")
        return False


# Hauptprogramm
print("YouTube Transcript & Audio Downloader")
print("=" * 150)

# URL oder Video-ID eingeben
url_input = input("\nBitte gib die YouTube-URL oder Video-ID ein: ").strip()

# Frage ob Audio heruntergeladen werden soll
download_audio_option = input("Möchtest du auch das Audio als MP3 herunterladen? (j/n): ").strip().lower()

try:
    # Extrahiere Video-ID
    video_id = extract_video_id(url_input)
    print(f"✓ Video-ID erkannt: {video_id}")

    # Hole Video-Titel
    print("Hole Video-Informationen...")
    video_title = get_video_info(video_id)
    print(f"✓ Video-Titel: {video_title}")

    # Erstelle sauberen Dateinamen
    base_filename = sanitize_filename(video_title)

    # Hole Transkript
    print("\nLade Transkript...")
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    # Suche nach deutschem oder englischem Transkript
    transcript = transcript_list.find_transcript(['de', 'en'])
    print(f"✓ Transkript gefunden: {transcript.language} ({transcript.language_code})")

    # Hole Transkript-Daten
    transcript_data = transcript.fetch()

    # Speichere als JSON
    json_formatter = JSONFormatter()
    json_formatted = json_formatter.format_transcript(transcript_data)
    json_filename = f"{base_filename}.json"

    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json_file.write(json_formatted)

    print(f"✓ JSON gespeichert: {json_filename}")

    # Erstelle lesbaren Text
    text_formatter = TextFormatter()
    text_output = text_formatter.format_transcript(transcript_data)

    # Formatiere Text mit Zeilenumbruch
    wrapped_text = textwrap.fill(text_output, width=150)

    # Speichere als Text
    text_filename = f"{base_filename}.txt"
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        text_file.write(wrapped_text)

    print(f"✓ Text gespeichert: {text_filename}")

    # Audio herunterladen wenn gewünscht
    if download_audio_option in ['j', 'ja', 'y', 'yes']:
        print("\n" + "=" * 150)
        audio_success = download_audio(video_id, base_filename)
        if audio_success:
            print(f"✓ Audio gespeichert: {base_filename}.mp3")

    # Zeige Vorschau
    print("\n" + "=" * 150)
    print("TRANSKRIPT (Vorschau):\n")
    print(wrapped_text[:500] + "..." if len(wrapped_text) > 500 else wrapped_text)
    print("\n" + "=" * 150)
    print("\n✓ Download abgeschlossen!")

except ValueError as e:
    print(f"\n✗ Fehler: {e}")
except Exception as e:
    print(f"\n✗ Fehler beim Abrufen des Transkripts: {e}")
    print("Mögliche Gründe:")
    print("  - Das Video hat kein Transkript")
    print("  - Das Video ist nicht verfügbar")
    print("  - Die Video-ID ist ungültig")