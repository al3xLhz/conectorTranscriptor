import subprocess
import os
from dotenv import load_dotenv
import time
import sys

load_dotenv()

class Docker:

    def __init__(self):
        self.status = False
        self.verificar_docker()
        if not self.status:
            self.iniciar_docker_desktop()
        self.contenedor_id = os.getenv("Contenedor_id")  # Valor por defecto
        self.nombre_contenedor = self.contenedor_id.split(":")[0]


    # --- Verificar si Docker está encendido ---
    def verificar_docker(self):
        try:
            resultado = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.status = resultado.returncode == 0
        except FileNotFoundError:
            print("❌ Docker no está instalado o en el PATH.")
            self.status = False

    def iniciar_docker_desktop(self):
        ruta_docker = os.getenv("Docker_path")
        if not ruta_docker or not os.path.exists(ruta_docker):
            print("❌ No se encontró Docker Desktop.")
            return
        print("⏳ Iniciando Docker Desktop...")
        subprocess.Popen([ruta_docker], shell=True)
        self.esperar_docker_activo()

    def esperar_docker_activo(self, timeout=60):
        print("⏳ Esperando que Docker esté listo...")
        for _ in range(timeout):
            self.verificar_docker()
            if self.status:
                print("✅ Docker está activo.")
                return True
            time.sleep(1)
        print("❌ Docker no se activó a tiempo.")
        return False

    # --- Verificar o crear contenedor ---
    def asegurar_contenedor(self):
        print(f"🔎 Verificando contenedor '{self.nombre_contenedor}'...")

        resultado = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={self.nombre_contenedor}", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )

        # Carpeta local correcta
        carpeta_local = os.path.join(os.getcwd(), "Audios")
        os.makedirs(carpeta_local, exist_ok=True)
        print(f"📂 Carpeta local: {carpeta_local}")
        # Si no existe el contenedor, crearlo
        if self.nombre_contenedor not in resultado.stdout:
            try:
                subprocess.run([
                    "docker", "run", "-d",
                    "--gpus", "all",  # ✅ habilita GPU
                    "--name", self.nombre_contenedor,
                    "-v", f"{carpeta_local}:/app/Audio",
                    "--restart", "unless-stopped",  # 🔁 reinicio automático
                    self.contenedor_id
                ], check=True)
                print("✅ Contenedor creado correctamente.")
                return "created"
            except subprocess.CalledProcessError as e:
                print(f"❌ Error al crear contenedor: {e}")
                sys.exit(1)
        else:
            print("✅ Contenedor existente detectado.")

        # Verificar si está corriendo
        estado = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", self.nombre_contenedor],
            capture_output=True, text=True
        ).stdout.strip()

        return "running" if estado == "true" else "stopped"


    # --- Ejecutar comando dentro del contenedor ---
    def ejecutar_en_contenedor(self, modo):
        if not self.status:
            print("🔧 Docker no está activo. Intentando iniciarlo...")
            self.iniciar_docker_desktop()
            if not self.status:
                print("❌ No se pudo iniciar Docker.")
                return

        estado = self.asegurar_contenedor()

        # Solo inicia si no está corriendo
        if estado == "stopped":
            print(f"📦 Iniciando contenedor '{self.nombre_contenedor}'...")
            subprocess.run(["docker", "start", self.nombre_contenedor], check=False)

        comando = f"python app.py --mode {modo}"
        print(f"🚀 Ejecutando comando en Docker: {comando}")

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        resultado = subprocess.run(
            ["docker", "exec", self.nombre_contenedor, "bash", "-c", comando],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=CREATE_NO_WINDOW
        )

        if resultado.returncode == 0:
            print("✅ Comando ejecutado correctamente.")
            return resultado.stdout.strip()
        else:
            print(f"⚠️ Error ejecutando comando:\n{resultado.stderr.strip()}")
            return resultado.stderr.strip()
