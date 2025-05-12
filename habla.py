#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Nota: Este script utiliza los comandos 'say' y 'open' que son específicos de macOS
# para la síntesis de voz y la apertura de imágenes.

import re
import time
import subprocess
import os
import glob # Módulo para encontrar archivos por patrón

start_time = time.time() # Tiempo de inicio global del script

# --- Funciones auxiliares ---

def speak(text_to_speak):
    """Utiliza el comando 'say' de macOS para la síntesis de voz."""
    if not text_to_speak or not text_to_speak.strip():
        return
    try:
        subprocess.run(["say", text_to_speak], check=True)
    except FileNotFoundError:
        print("Error: Comando 'say' no encontrado. Este script requiere macOS para la síntesis de voz.")
    except subprocess.CalledProcessError as e:
        print(f"Error durante la ejecución de 'say': {e}")

# --- Funciones principales ---

def sintetizar_tiempo():
    """Sintetiza por voz los minutos transcurridos desde el inicio del script."""
    current_time = time.time()
    elapsed_seconds = current_time - start_time
    elapsed_minutes = int(elapsed_seconds / 60)
    message = f"Han transcurrido {elapsed_minutes} minutos desde el inicio de la ejecución"
    print(message)
    speak(message)

def manejar_pausa(pause_duration_str, text_content):
    """Maneja la pausa, opcionalmente diciendo un texto antes."""
    if text_content:
        speak(text_content)
    
    try:
        pause_duration_int = int(pause_duration_str)
        print(f"Esperando {pause_duration_int} segundos...")
        speak(f"{pause_duration_int} segundos")
        time.sleep(pause_duration_int)
    except ValueError:
        print(f"Error: Duración de pausa inválida '{pause_duration_str}'")

def manejar_imagen(image_filename, text_content):
    """Maneja la imagen, opcionalmente diciendo un texto antes."""
    if text_content:
        speak(text_content)
    
    print(f"Abriendo la imagen {image_filename}...")
    try:
        subprocess.run(["open", image_filename], check=True)
    except FileNotFoundError:
        print(f"Error: Comando 'open' no encontrado (requiere macOS) o no se pudo abrir '{image_filename}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error al abrir la imagen '{image_filename}': {e}")

def manejar_ejercicio(ejercicio_numero):
    """Maneja el anuncio del número de ejercicio."""
    message = f"Ejercicio {ejercicio_numero}"
    print(message)
    speak(message)

# --- Lógica principal de procesamiento ---

def main(input_filename):
    """Función principal que lee y procesa el archivo de entrada."""
    
    # Aunque seleccionemos de una lista, una comprobación extra no hace daño.
    if not os.path.exists(input_filename):
        print(f"Error: El archivo de entrada '{input_filename}' no fue encontrado al intentar procesarlo.")
        return

    print(f"Procesando el archivo: {input_filename}")
    print("--------------------------------------------------------------------")
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            for line_number, line_content in enumerate(f, 1):
                line_content = line_content.strip()
                if not line_content:
                    continue

                parts = line_content.split('/')
                
                for part_text in parts:
                    part = part_text.strip()
                    if not part:
                        continue

                    match_pause = re.search(r"\[PAUSE:(\d+)\](.*)", part)
                    if match_pause:
                        duration = match_pause.group(1)
                        text_after_marker = match_pause.group(2).strip()
                        manejar_pausa(duration, text_after_marker)
                        continue 
                    
                    match_imagen = re.search(r"\[IMAGEN:\s*([^\]]+)\]", part)
                    if match_imagen:
                        image_filename = match_imagen.group(1).strip()
                        text_before_tag = ""
                        tag_start_index = match_imagen.start(0)
                        if tag_start_index > 0:
                            text_before_tag = part[:tag_start_index].strip()
                        manejar_imagen(image_filename, text_before_tag)
                        continue
                    
                    match_tiempo = re.search(r"\[TIEMPO\]", part)
                    if match_tiempo:
                        sintetizar_tiempo()
                        continue
                    
                    match_ejercicio = re.search(r"\[EJERCICIO:\s*(\d+)\]", part)
                    if match_ejercicio:
                        numero = match_ejercicio.group(1).strip()
                        manejar_ejercicio(numero)
                        continue
                    
                    speak(part)

    except Exception as e:
        print(f"Ocurrió un error inesperado durante la ejecución: {e}")

if __name__ == "__main__":
    print("Iniciando el script de Pilates en Python...")
    print("--------------------------------------------------------------------")
    print("Nota: Este script utiliza los comandos 'say' y 'open' de macOS.")
    
    # Listar archivos .txt en el directorio actual
    txt_files = glob.glob("*.txt")
    # Alternativa más explícita si se quieren solo archivos y no directorios (glob suele ser suficiente):
    # txt_files = [f for f in os.listdir('.') if os.path.isfile(f) and f.lower().endswith('.txt')]
    
    if not txt_files:
        print("No se encontraron archivos .txt en el directorio actual.")
        print("Por favor, asegúrate de que haya archivos .txt o introduce la ruta manualmente.")
        # Opcionalmente, podrías volver a pedir una ruta manual aquí:
        # manual_file = input("Introduce la ruta completa al archivo .txt: ")
        # if manual_file and os.path.exists(manual_file):
        #    main(manual_file)
        # else:
        #    print("Archivo no válido o no encontrado. Saliendo.")
    else:
        print("\nArchivos .txt disponibles en el directorio actual:")
        for i, filename in enumerate(txt_files):
            print(f"  {i + 1}. {filename}")
        
        selected_filename = None
        while True:
            try:
                choice_str = input(f"\nElige el número del archivo a procesar (1-{len(txt_files)}): ")
                choice_int = int(choice_str)
                if 1 <= choice_int <= len(txt_files):
                    selected_filename = txt_files[choice_int - 1]
                    break
                else:
                    print(f"Selección inválida. Por favor, introduce un número entre 1 y {len(txt_files)}.")
            except ValueError:
                print("Entrada inválida. Por favor, introduce un número.")
            except KeyboardInterrupt:
                print("\nSelección cancelada por el usuario. Saliendo.")
                break # Sale del bucle while
        
        if selected_filename:
            main(selected_filename)
        else:
            if not txt_files: # Si no había archivos y no se seleccionó manualmente
                pass # El mensaje ya se mostró
            else: # Si se canceló la selección
                print("No se seleccionó ningún archivo.")

    print("--------------------------------------------------------------------")
    print("Script de Pilates finalizado.")