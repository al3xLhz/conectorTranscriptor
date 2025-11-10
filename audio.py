import sounddevice as sd
from datetime import datetime
from scipy.io.wavfile import write, read
import numpy as np
import soundfile as sf
import os
import shutil
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
import threading
from utils import audio_to_wav, video_to_wav
load_dotenv()

TranscriptIA_Path = "Audios"

class Audio:

    def __init__(self):
        self.frecuencia_muestreo = 44100
        self.canales = 2
        self.buffer = []
        self.stream = None
        self.esta_grabando = False
        self.esta_pausado = False
        self.hilo = None

    def _callback(self, indata, frames, time, status):
        if self.esta_grabando and not self.esta_pausado:
            self.buffer.append(indata.copy())

    def iniciar_grabacion(self):
        if self.esta_grabando:
            print("⚠️ Ya se está grabando.")
            return

        print("🎤 Iniciando grabación")
        self.buffer = []
        self.esta_grabando = True
        self.esta_pausado = False
        self.nombre_archivo = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        self.stream = sd.InputStream(samplerate=self.frecuencia_muestreo, channels=self.canales, callback=self._callback)
        self.hilo = threading.Thread(target=self._grabar)
        self.hilo.start()

    def _grabar(self):
        with self.stream:
            while self.esta_grabando:
                sd.sleep(100)

    def pausar_grabacion(self):
        if self.esta_grabando:
            self.esta_pausado = True
            print("⏸ Grabación pausada")

    def reanudar_grabacion(self):
        if self.esta_grabando and self.esta_pausado:
            self.esta_pausado = False
            print("▶️ Grabación reanudada")

    def stop_grabacion(self):
        if not self.esta_grabando:
            print("⚠️ No hay grabación activa.")
            return

        print("🛑 Deteniendo grabación")
        self.esta_grabando = False
        self.hilo.join()

        if not self.buffer:
            print("⚠️ No se grabó nada.")
            return

        audio = np.concatenate(self.buffer)
        audio = self.quitar_silencios(audio_brute=audio)
        # Normalizar el audio para evitar distorsión
        audio_limpio = audio / np.max(np.abs(audio))
        #print(f"✅ Audio guardado en: {f"Audios/{self.nombre_archivo}"}")


        if audio_limpio is None or audio_limpio.size == 0:
            print("⚠️ Todo el audio es silencio o muy bajo.")
            return

        os.makedirs("Audios", exist_ok=True)
        ruta = f"Audios/{self.nombre_archivo}"
        write(ruta, self.frecuencia_muestreo, audio_limpio.astype(np.float32))
        print(f"✅ Audio guardado en: {ruta}")

    def cargar_audio(self):
        # Crear ventana oculta (no se mostrará al usuario)
        root = tk.Tk()
        root.withdraw()

        # Abrir ventana de selección de archivo
        ruta_archivo = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=[
                ("Archivos de audio", "*.dat.unknown *.opus *.m4a *.ogg *.wav *.mp3"),
                ("Todos los archivos", "*.*")
            ]
        )

        #print("ruta_archivo", ruta_archivo)
        if not ruta_archivo:
            print("No se seleccionó ningún archivo")
            return False

        ruta_archivo_wav = audio_to_wav(ruta_archivo)
        name_audio = ruta_archivo_wav.split("\\")[-1]
        name_audio = name_audio.split(".")[0]

        print(f"Cargando audio: {name_audio}")
        # 3. Leer WAV y convertir a onda
        data, samplerate = sf.read(ruta_archivo_wav, dtype='float32')
        data = data.astype(np.float32)
        audio_limpio = self.quitar_silencios(audio_brute = data)
        # Guardar audio limpio
        write(ruta_archivo_wav, samplerate, audio_limpio)
        #print(f"Audio limpio guardado en: {ruta_wav}")

        if ruta_archivo_wav:
            os.makedirs(TranscriptIA_Path, exist_ok=True)
            shutil.copy(ruta_archivo_wav, TranscriptIA_Path)
            os.remove(ruta_archivo_wav)
            if ruta_archivo and ruta_archivo != ruta_archivo_wav:
                os.remove(ruta_archivo)
            return True

        root.destroy()

    def cargar_video(self):
        # Crear ventana oculta (no se mostrará al usuario)
        root = tk.Tk()
        root.withdraw()

        # Abrir ventana de selección de archivo
        ruta_archivo = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=[
                ("Archivos de video", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("Todos los archivos", "*.*")
            ]
        )

        #print("ruta_archivo", ruta_archivo)
        if not ruta_archivo:
            print("No se seleccionó ningún archivo")
            return False

        ruta_archivo_wav = video_to_wav(ruta_archivo)
        name_audio = ruta_archivo_wav.split("\\")[-1]
        name_audio = name_audio.split(".")[0]

        print(f"Cargando audio: {name_audio}")
        # 3. Leer WAV y convertir a onda
        data, samplerate = sf.read(ruta_archivo_wav, dtype='float32')
        data = data.astype(np.float32)
        audio_limpio = self.quitar_silencios(audio_brute = data)
        # Guardar audio limpio
        write(ruta_archivo_wav, samplerate, audio_limpio)
        #print(f"Audio limpio guardado en: {ruta_wav}")

        if ruta_archivo_wav:
            os.makedirs(TranscriptIA_Path, exist_ok=True)
            shutil.copy(ruta_archivo_wav, TranscriptIA_Path)
            os.remove(ruta_archivo_wav)
            return True

        if ruta_archivo:
            #os.remove(ruta_archivo)
            pass

        root.destroy()

    def quitar_silencios(self, input_audio=None, audio_brute=None, threshold=0.006, frame_size=256, margen=6):
        if audio_brute is not None:
            audio = audio_brute
        elif input_audio:
            import soundfile as sf
            audio, _ = sf.read(input_audio)
        else:
            return None

        if audio.ndim == 2:
            audio = audio.mean(axis=1)

        frames = [audio[i:i + frame_size] for i in range(0, len(audio), frame_size)]

        # Identificar índices de frames con sonido
        indices_sonido = [i for i, f in enumerate(frames) if np.sqrt(np.mean(f ** 2)) > threshold]

        if not indices_sonido:
            return np.array([])

        # Expandir índices para incluir margen antes y después
        indices_expandidos = set()
        for idx in indices_sonido:
            for i in range(idx - margen, idx + margen + 1):
                if 0 <= i < len(frames):
                    indices_expandidos.add(i)

        # Reconstruir audio filtrado
        frames_filtrados = [frames[i] for i in sorted(indices_expandidos)]
        audio_filtrado = np.concatenate(frames_filtrados)

        return audio_filtrado












