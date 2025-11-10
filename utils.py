import os
import subprocess

def limpiar_resultado_transcript(resultado):
    lineas = resultado.split("\n")
    #print(lineas)
    #print(len(lineas))
    transcript_completa = lineas[3]
    transcript_limpio = transcript_completa.replace("Transcripción final: ", "")

    return transcript_limpio

def promptear_transcript(transcript):
    prompt = f"""{transcript}
    """
    return prompt


def convertir_a_wav(input_file):
    # Obtiene la ruta y nombre base del archivo original, y cambia la extensión a .wav
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.dirname(input_file)
    output_file = os.path.join(output_dir, f"{base_name}.wav")

    command = [
        "ffmpeg",
        "-y",              # sobrescribe si existe
        "-i", input_file,  # entrada
        output_file        # salida
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #os.remove(input_file)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error al convertir {input_file} a WAV: {e}")
        return "ERROR"
    except FileNotFoundError:
        print("ffmpeg no está instalado o no se encuentra en el PATH del sistema.")
        return "ERROR"

def audio_to_wav(audio_path):
    if not os.path.isfile(audio_path):
        print("El archivo no existe.")
        return "ERROR"

    ext = os.path.splitext(audio_path)[1].lower()
    
    if ext in [".m4a", ".opus", ".ogg", ".mp3"]:
        return convertir_a_wav(audio_path)
    elif ext == ".wav":
        return audio_path
    else:
        print("Formato no compatible")
        return "ERROR"
    
def video_to_wav(video_path):
    if not os.path.isfile(video_path):
        print("El archivo no existe.")
        return "ERROR"
    
    ext = os.path.splitext(video_path)[1].lower()
    if ext in [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]:
        return convertir_a_wav(video_path)
    else:
        print("Formato no compatible")
        return "ERROR"