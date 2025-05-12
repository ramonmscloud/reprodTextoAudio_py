#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Nota: Este script utiliza los comandos 'say' y 'open' que son específicos de macOS
# para la síntesis de voz y la apertura de imágenes, con el fin de replicar
# la funcionalidad del script Zsh original.
# Si necesitas una versión más portable (multiplataforma), se requerirían
# bibliotecas como pyttsx3 para TTS y webbrowser o Pillow para imágenes.

import re
import time
import subprocess
import os # Solo para os.path.exists en una comprobación opcional

INPUT_FILE = "pilates01.txt"
start_time = time.time()

# --- Funciones auxiliares ---

def speak(text_to_speak):
    """Utiliza el comando 'say' de macOS para la síntesis de voz."""
    if not text_to_speak or not text_to_speak.strip():
        return  # No ejecutar 'say' con una cadena vacía o solo espacios
    try:
        # Descomenta la siguiente línea para depurar lo que se está intentando decir:
        # print(f"DEBUG: Intentando decir: '{text_to_speak}'")
        subprocess.run(["say", text_to_speak], check=True)
    except FileNotFoundError:
        print("Error: Comando 'say' no encontrado. Este script requiere macOS para la síntesis de voz.")
    except subprocess.CalledProcessError as e:
        print(f"Error durante la ejecución de 'say': {e}")

# --- Funciones principales (equivalentes a las del script Zsh) ---

def sintetizar_tiempo():
    """Sintetiza por voz los minutos transcurridos."""
    current_time = time.time()
    elapsed_seconds = current_time - start_time
    elapsed_minutes = int(elapsed_seconds / 60)
    message = f"Han transcurrido {elapsed_minutes} minutos desde el inicio de la ejecución"
    print(message) # Imprime en consola primero, como en el script original
    speak(message)

def manejar_pausa(pause_duration_str, text_content):
    """Maneja la pausa, opcionalmente diciendo un texto antes."""
    if text_content: # Si hay texto asociado (lo que venía después de [PAUSE:X])
        speak(text_content)
    
    try:
        pause_duration_int = int(pause_duration_str)
        # El script original imprimía "Esperando X segundos..." y luego decía "X segundos"
        print(f"Esperando {pause_duration_int} segundos...")
        speak(f"{pause_duration_int} segundos")
        time.sleep(pause_duration_int)
    except ValueError:
        print(f"Error: Duración de pausa inválida '{pause_duration_str}'")

def manejar_imagen(image_filename, text_content):
    """Maneja la imagen, opcionalmente diciendo un texto antes."""
    if text_content: # Si hay texto asociado (lo que venía antes de IMAGEN:)
        speak(text_content)
    
    print(f"Abriendo la imagen {image_filename}...")
    try:
        # Utiliza el comando 'open' de macOS
        subprocess.run(["open", image_filename], check=True)
        # Opcionalmente, podrías añadir una comprobación de si el archivo existe antes de intentar abrirlo:
        # if not os.path.exists(image_filename):
        #     print(f"Advertencia: El archivo de imagen '{image_filename}' no parece existir.")
    except FileNotFoundError:
        # Esto ocurriría si el comando 'open' no se encuentra, o si 'open' falla porque el archivo no existe (depende de 'open')
        print(f"Error: Comando 'open' no encontrado (requiere macOS) o no se pudo abrir '{image_filename}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error al abrir la imagen '{image_filename}': {e}")

def manejar_ejercicio(ejercicio_numero):
    """Maneja el anuncio del número de ejercicio."""
    message = f"Ejercicio {ejercicio_numero}"
    print(message) # Imprime en consola primero
    speak(message)

# --- Lógica principal de procesamiento ---

def main():
    """Función principal que lee y procesa el archivo de entrada."""
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line_number, line_content in enumerate(f, 1):
                line_content = line_content.strip()
                if not line_content: # Saltar líneas vacías
                    continue

                # Dividir la línea en partes usando '/' como en el script Zsh
                parts = line_content.split('/')
                
                for part_text in parts:
                    part = part_text.strip()
                    if not part: # Saltar partes vacías resultantes del split
                        continue

                    # Intentar encontrar y procesar los marcadores
                    # La lógica if/elif/else asegura que solo un tipo de marcador se procese por parte

                    # 1. [PAUSE:X]TextoOpcionalDespues
                    # Zsh: PAUSE:([0-9]+)](.*)
                    match_pause = re.search(r"\[PAUSE:(\d+)\](.*)", part)
                    if match_pause:
                        duration = match_pause.group(1)
                        text_after_marker = match_pause.group(2).strip()
                        manejar_pausa(duration, text_after_marker)
                    
                    # 2. TextoOpcionalAntes[IMAGEN:archivo.png]
                    # Zsh: IMAGEN:\ (.+)]  y texto con "${part%%IMAGEN:*}"
                    elif re.search(r"\[IMAGEN:\s*([^\]]+)\]", part): # Usar re.search aquí para la condición elif
                        match_imagen = re.search(r"\[IMAGEN:\s*([^\]]+)\]", part) # Obtener el objeto match
                        image_filename = match_imagen.group(1).strip()
                        
                        # Replicar la lógica de Zsh "${part%%IMAGEN:*}"
                        # Esto toma el texto ANTES de la primera aparición de "IMAGEN:"
                        text_to_speak_for_image = ""
                        idx = part.find("IMAGEN:") # Encuentra el inicio de "IMAGEN:"
                        if idx != -1:
                            text_to_speak_for_image = part[:idx].strip() # Texto antes, sin espacios extra al final
                        
                        manejar_imagen(image_filename, text_to_speak_for_image)
                    
                    # 3. [TIEMPO]
                    elif re.search(r"\[TIEMPO\]", part):
                        sintetizar_tiempo()
                    
                    # 4. [EJERCICIO:N]
                    # Zsh: EJERCICIO:\ ([0-9]+)]
                    elif re.search(r"\[EJERCICIO:\s*(\d+)\]", part):
                        match_ejercicio = re.search(r"\[EJERCICIO:\s*(\d+)\]", part) # Obtener el objeto match
                        numero = match_ejercicio.group(1).strip()
                        manejar_ejercicio(numero)
                    
                    # 5. Si no es ninguno de los marcadores, decir la parte entera
                    else:
                        speak(part)

    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{INPUT_FILE}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la ejecución: {e}")

if __name__ == "__main__":
    print("Iniciando el script de Pilates en Python...")
    print("--------------------------------------------------------------------")
    print("Nota: Este script utiliza los comandos 'say' y 'open' de macOS.")
    print("Asegúrate de que el archivo 'pilates01.txt' esté en el mismo directorio.")
    print("--------------------------------------------------------------------")
    main()
    print("--------------------------------------------------------------------")
    print("Script de Pilates finalizado.")º