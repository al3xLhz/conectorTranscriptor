from ventana import Ventana

"""
def procesar_argumentos():
    # Valores por defecto
    accion = "cargar"
    modo = "turbo"
    # No hay argumentos: usar valores por defecto
    if len(sys.argv) == 1:
        print("ℹ️ Ejecutando en modo por defecto: '-c --mode turbo'")
        return accion, modo
    
    args = sys.argv[1:]

    for i, arg in enumerate(args):
        if arg in ["-g", "--grabar"]:
            accion = "grabar"
        elif arg in ["-c", "--cargar"]:
            accion = "cargar"
        elif arg == "--mode" and i + 1 < len(args):
            modo_valido = args[i + 1].lower()
            if modo_valido in ["turbo", "large"]:
                modo = modo_valido
            else:
                print(f"❌ Modo no válido: {modo_valido}. Usando modo por defecto 'turbo'.")
        elif arg.startswith("--mode="):
            modo_valido = arg.split("=")[1].lower()
            if modo_valido in ["turbo", "large"]:
                modo = modo_valido
            else:
                print(f"❌ Modo no válido: {modo_valido}. Usando modo por defecto 'turbo'.")

    return accion, modo
"""
def main():
    ventana = Ventana()
    ventana.mainloop()


if __name__ == "__main__":
    main()




