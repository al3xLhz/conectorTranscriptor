import tkinter as tk
from tkinter import messagebox
from audio import Audio
from docker import Docker
from tkinter import font
import threading
import sys
from utils import limpiar_resultado_transcript, promptear_transcript
import pyperclip
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

TranscriptIA_Path = "Audios"


class Ventana:

    def __init__(self):
        self.docker = Docker()
        self.audio = Audio()
        self.modo = "turbo"

        # Variables para el movimiento de ventana
        self._x_inicio = 0
        self._y_inicio = 0
        self._x_ventana = 0
        self._y_ventana = 0
        # Quitar barra de título y botones de ventana
        self.ventana = tk.Tk()
        #self.ventana.overrideredirect(True)
        self.ventana.resizable(True, False)
        self.ventana.geometry("500x500")
        self.ventana.configure(bg="white")
        self.ventana.bind("<Button-1>", self.iniciar_movimiento)
        self.ventana.bind("<B1-Motion>", self.mover_ventana)
        # Centrar la ventana
        # Variables de control
        self.ventana_grabacion = None
        self.grabando = False
        self.centrar_ventana()
        self.ventana_principal()

    def iniciar_movimiento(self, event):
        self._x_inicio = event.x_root
        self._y_inicio = event.y_root
        self._x_ventana = self.ventana.winfo_x()
        self._y_ventana = self.ventana.winfo_y()

    def mover_ventana(self, event):
        dx = event.x_root - self._x_inicio
        dy = event.y_root - self._y_inicio
        nuevo_x = self._x_ventana + dx
        nuevo_y = self._y_ventana + dy
        self.ventana.geometry(f"+{nuevo_x}+{nuevo_y}")

    def mainloop(self):
        self.ventana.mainloop()

    def cerrar(self):
        """Cierra la aplicación"""
        try:
            # Detener grabación si está activa
            if self.grabando:
                self.audio.stop_grabacion()

            # Cerrar ventana de grabación si existe
            if self.ventana_grabacion and self.ventana_grabacion.winfo_exists():
                self.ventana_grabacion.destroy()

        except Exception as e:
            print(f"Error al cerrar: {e}")
        finally:
            self.ventana.destroy()
            sys.exit(1)

    def centrar_ventana(self, ancho=500, alto=500):
        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def ventana_principal(self):
        fuente = font.Font(size=10)

        # Frame contenedor
        self.marco = tk.Frame(self.ventana, bg="white")
        self.marco.pack(expand=True,fill="both")

        # Etiqueta de modo
        lbl_modo = tk.Label(self.marco, text="Modo:", font=fuente, bg="white")
        lbl_modo.pack(pady=(20, 5))

        # Variable para el modo
        self.var_modo = tk.StringVar(value="turbo")

        # ComboBox de modo
        combo_modo = tk.OptionMenu(self.marco, self.var_modo, "turbo", "large")
        combo_modo.config(width=10, font=fuente)
        combo_modo.pack(pady=5)

        # Separador
        separador = tk.Frame(self.marco, height=2, bg="lightgray")
        separador.pack(fill="x", padx=50, pady=20)

        # Botón grabar
        self.btn_grabar = tk.Button(self.marco, text="🎤 Grabar Audio",
                                    font=fuente, width=20,
                                    command=self.mostrar_controles_grabadora)
        self.btn_grabar.pack(pady=(10, 10), ipadx=4)

        # Botón cargar
        self.btn_cargar = tk.Button(self.marco, text="🎙️ Cargar Audio",
                                    font=fuente, width=20,
                                    command=self.cargar_audio)
        self.btn_cargar.pack(pady=(0, 10), ipadx=4)

        self.btn_cargar_video = tk.Button(self.marco, text="📹 Cargar Video",
                                    font=fuente, width=20,
                                    command=self.cargar_video)
        self.btn_cargar_video.pack(pady=(0, 10), ipadx=4)

        # Botón procesar
        self.btn_procesar = tk.Button(self.marco, text="🔄 Procesar",
                                        font=fuente, width=20,
                                        command=self.procesar_audio)
        self.btn_procesar.pack(pady=(0, 10), ipadx=4)

        # Etiqueta de estado
        self.lbl_estado = tk.Label(self.marco, text="Listo para procesar audio",
                                    font=fuente, bg="white", fg="green")
        self.lbl_estado.pack(pady=(10, 10))

        # Separador
        separador2 = tk.Frame(self.marco, height=2, bg="lightgray")
        separador2.pack(fill="x", padx=50, pady=10)

        # Botón cerrar
        btn_cerrar = tk.Button(self.marco, text="❌ Cerrar",
                                font=fuente, width=20,
                                command=self.cerrar)
        btn_cerrar.pack(pady=(10, 20), ipadx=4)

    def actualizar_estado(self, mensaje, color="blue"):
        """Actualiza el estado mostrado en la interfaz"""
        self.lbl_estado.config(text=mensaje, fg=color)

    def cargar_audio(self):
        """Maneja la carga de archivos de audio"""
        try:
            self.actualizar_estado("Cargando archivo...", "orange")
            resultado = self.audio.cargar_audio()
            if resultado:
                self.actualizar_estado("✅ Archivo cargado correctamente", "green")
            else:
                self.actualizar_estado("❌ Error al cargar archivo", "red")
        except Exception as e:
            self.actualizar_estado(f"❌ Error: {str(e)}", "red")
            print(f"Error al cargar audio: {e}")
            traceback.print_exc()

    def cargar_video(self):
        """Maneja la carga de archivos de video"""
        try:
            self.actualizar_estado("Cargando archivo...", "orange")
            resultado = self.audio.cargar_video()
            if resultado:
                self.actualizar_estado("✅ Archivo cargado correctamente", "green")
        except Exception as e:
            self.actualizar_estado(f"❌ Error: {str(e)}", "red")
            print(f"Error al cargar video: {e}")
            traceback.print_exc()

    def procesar_audio(self):
        """Procesa el audio en un hilo separado"""

        # Deshabilitar botones durante el procesamiento
        self.btn_procesar.config(state="disabled")
        self.btn_cargar.config(state="disabled")
        self.btn_grabar.config(state="disabled")

        # Ejecutar procesamiento en hilo separado
        threading.Thread(target=self._procesar_audio_en_hilo, daemon=True).start()

    def limpiar_ventana(self):
        for widget in self.marco.winfo_children():
            widget.destroy()

    def volver_a_inicio(self):
        self.marco.destroy()
        self.ventana_principal()

    #def procesar_audio(self):
    #    # Ejecutar procesamiento en hilo
    #    threading.Thread(target=self._procesar_audio_en_hilo).start()

    def _procesar_audio_en_hilo(self):
        """Ejecuta el procesamiento de audio en un hilo separado"""
        try:
            self.ventana.after(0, lambda: self.actualizar_estado("🔄 Procesando audio...", "orange"))
            resultado = self.docker.ejecutar_en_contenedor(
                modo=self.var_modo.get()
            )
            print("resultado: ", resultado)

            print("--------------------------------")

            if 'No audio' in resultado:
                self.ventana.after(0, lambda: messagebox.showinfo("❌ Error", "No se detectó audio en el archivo"))
                self.ventana.after(0, lambda: self.actualizar_estado("❌ No se detectó archivo de audio", "red"))
                return

            # Limpiar y procesar el resultado
            transcript = limpiar_resultado_transcript(resultado)

            prompt = promptear_transcript(transcript)
            #print("prompt: ", prompt)

            # Copiar al portapapeles
            pyperclip.copy(prompt)

            # Mostrar resultado y actualizar estado
            # Llamar la función completa en el hilo principal
            self.ventana.after(0, self.mostrar_info_y_preguntar(prompt))

            self.ventana.after(0, lambda: self.actualizar_estado("✅ Texto copiado al portapapeles", "green"))

        except Exception as e:
            error_msg = str(e)
            self.ventana.after(0, lambda: messagebox.showerror("❌ Error", f"Error al procesar: {error_msg}"))
            self.ventana.after(0, lambda: self.actualizar_estado(f"❌ Error: {error_msg}", "red"))
            print(f"Error en procesamiento: {e}")
            traceback.print_exc()
        finally:
            # Rehabilitar botones
            self.ventana.after(0, self._rehabilitar_botones)

    def _rehabilitar_botones(self):
        """Rehabilita los botones después del procesamiento"""
        self.btn_procesar.config(state="normal")
        self.btn_cargar.config(state="normal")
        self.btn_grabar.config(state="normal")

    def mostrar_controles_grabadora(self):
        """Muestra la ventana de controles de grabación"""
        if self.ventana_grabacion and self.ventana_grabacion.winfo_exists():
            self.ventana_grabacion.lift()
            return

        # Crear nueva ventana de grabación
        self.ventana_grabacion = tk.Toplevel(self.ventana)
        self.ventana_grabacion.title("🎙️ Grabando Audio")
        self.ventana_grabacion.configure(bg="white")
        self.ventana_grabacion.resizable(False, False)
        self.ventana_grabacion.geometry("400x300")
        self.ventana_grabacion.transient(self.ventana)  # Mantener encima de la ventana principal

        # Centrar ventana de grabación
        self.centrar_ventana_grabacion()

        # Marco para los controles
        marco_grabacion = tk.Frame(self.ventana_grabacion, bg="white")
        marco_grabacion.pack(expand=True, fill="both", pady=20)

        # Título
        lbl_titulo = tk.Label(marco_grabacion, text="🔴 GRABANDO",
                                font=font.Font(size=16, weight="bold"),
                                bg="white", fg="red")
        lbl_titulo.pack(pady=(20, 30))

        # Estado de grabación
        self.lbl_estado_grabacion = tk.Label(marco_grabacion, text="Grabación en curso...",
                                            font=font.Font(size=12), bg="white", fg="green")
        self.lbl_estado_grabacion.pack(pady=(0, 20))

        # Botones de control
        btn_pausar = tk.Button(marco_grabacion, text="⏸️ Pausar",
                                font=("Arial", 12), width=15,
                                command=self.pausar_grabacion)
        btn_pausar.pack(pady=5)

        btn_reanudar = tk.Button(marco_grabacion, text="▶️ Reanudar",
                                font=("Arial", 12), width=15,
                                command=self.reanudar_grabacion)
        btn_reanudar.pack(pady=5)

        btn_stop = tk.Button(marco_grabacion, text="⏹️ Detener",
                            font=("Arial", 12), width=15,
                            command=self.detener_grabacion)
        btn_stop.pack(pady=5)

        # Protocolo de cierre
        self.ventana_grabacion.protocol("WM_DELETE_WINDOW", self.detener_grabacion)

        # Iniciar la grabación
        try:
            self.audio.iniciar_grabacion()
            self.grabando = True
            self.actualizar_estado("🔴 Grabando audio...", "red")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la grabación: {e}")
            self.ventana_grabacion.destroy()

    def centrar_ventana_grabacion(self):
        """Centra la ventana de grabación"""
        ancho, alto = 400, 300
        pantalla_ancho = self.ventana_grabacion.winfo_screenwidth()
        pantalla_alto = self.ventana_grabacion.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.ventana_grabacion.geometry(f"{ancho}x{alto}+{x}+{y}")

    def pausar_grabacion(self):
        """Pausa la grabación"""
        try:
            self.audio.pausar_grabacion()
            self.lbl_estado_grabacion.config(text="⏸️ Grabación pausada", fg="orange")
        except Exception as e:
            messagebox.showerror("Error", f"Error al pausar: {e}")

    def reanudar_grabacion(self):
        """Reanuda la grabación"""
        try:
            self.audio.reanudar_grabacion()
            self.lbl_estado_grabacion.config(text="🔴 Grabación en curso...", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Error al reanudar: {e}")

    def detener_grabacion(self):
        """Detiene la grabación y cierra la ventana"""
        try:
            if self.grabando:
                self.audio.stop_grabacion()
                self.grabando = False
                self.actualizar_estado("✅ Grabación completada", "green")

            if self.ventana_grabacion and self.ventana_grabacion.winfo_exists():
                self.ventana_grabacion.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al detener grabación: {e}")
            print(f"Error al detener grabación: {e}")

    def mostrar_info_y_preguntar(self, transcript):
        messagebox.showinfo("✅ Procesado", transcript)
        respuesta = messagebox.askyesno("🗑️ Borrar archivo", "¿Deseas borrar el archivo de audio procesado?")

        if respuesta:
            try:
                archivos = os.listdir(TranscriptIA_Path)
                if archivos:
                    primer_archivo = os.path.join(TranscriptIA_Path, archivos[0])
                    os.remove(primer_archivo)
                self.ventana.after(0, lambda: self.actualizar_estado("🗑️ Archivo borrado", "blue"))
            except Exception as e:
                self.ventana.after(0, lambda: messagebox.showerror("❌ Error", f"Error al borrar archivo: {str(e)}"))

        self.ventana.after(0, lambda: self.actualizar_estado("✅ Texto copiado al portapapeles", "green"))


