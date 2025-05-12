#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Nota: Este script utiliza los comandos 'say', 'open' y 'afplay' que son específicos de macOS
# para la síntesis de voz, la apertura de imágenes y la reproducción de audio.

import re
import time
import subprocess
import os
import glob # Módulo para encontrar archivos por patrón
import atexit # Para registrar funciones que se ejecutan al salir

start_time = time.time() # Tiempo de inicio global del script

# Variable global para manejar el proceso de la música de fondo
music_process = None

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

def start_background_music(audio_file_path):
    """Inicia la reproducción de música de fondo usando 'afplay' en macOS."""
    global music_process
    if not audio_file_path:
        return False
    if not os.path.exists(audio_file_path):
        print(f"Advertencia: Archivo de música no encontrado en '{audio_file_path}'. No se reproducirá música.")
        return False

    print(f"Intentando reproducir música de fondo: {os.path.basename(audio_file_path)}")
    try:
        music_process = subprocess.Popen(
            ["afplay", audio_file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("Música de fondo iniciada (se reproducirá una vez).")
        return True
    except FileNotFoundError:
        print("Error: 'afplay' (reproductor de audio de macOS) no encontrado. No se puede reproducir música de fondo.")
    except Exception as e:
        print(f"Error al iniciar la música de fondo: {e}")
    return False

def stop_background_music():
    """Detiene la música de fondo si se está reproduciendo."""
    global music_process
    if music_process and music_process.poll() is None:
        print("Deteniendo la música de fondo...")
        try:
            music_process.terminate()
            try:
                music_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print("La música de fondo no terminó a tiempo, forzando cierre...")
                music_process.kill()
            print("Música de fondo detenida.")
        except Exception as e:
            print(f"Error al detener la música de fondo: {e}")
        finally:
            music_process = None

atexit.register(stop_background_music)

# --- Funciones principales ---

def sintetizar_tiempo():
    current_time = time.time()
    elapsed_seconds = current_time - start_time
    elapsed_minutes = int(elapsed_seconds / 60)
    message = f"Han transcurrido {elapsed_minutes} minutos desde el inicio de la ejecución"
    print(message)
    speak(message)

def manejar_pausa(pause_duration_str, text_content):
    if text_content: speak(text_content)
    try:
        pause_duration_int = int(pause_duration_str)
        print(f"Esperando {pause_duration_int} segundos...")
        speak(f"{pause_duration_int} segundos")
        time.sleep(pause_duration_int)
    except ValueError:
        print(f"Error: Duración de pausa inválida '{pause_duration_str}'")

def manejar_imagen(image_filename, text_content):
    if text_content: speak(text_content)
    print(f"Abriendo la imagen {image_filename}...")
    try:
        subprocess.run(["open", image_filename], check=True)
    except FileNotFoundError:
        print(f"Error: Comando 'open' no encontrado o no se pudo abrir '{image_filename}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error al abrir la imagen '{image_filename}': {e}")

def manejar_ejercicio(ejercicio_numero):
    message = f"Ejercicio {ejercicio_numero}"
    print(message)
    speak(message)

# --- Lógica principal de procesamiento ---

def main(input_filename):
    if not os.path.exists(input_filename):
        print(f"Error: El archivo de entrada '{input_filename}' no fue encontrado al intentar procesarlo.")
        return

    print(f"Procesando el archivo de Pilates: {input_filename}")
    print("--------------------------------------------------------------------")
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            for line_number, line_content in enumerate(f, 1):
                line_content = line_content.strip()
                if not line_content: continue
                parts = line_content.split('/')
                for part_text in parts:
                    part = part_text.strip()
                    if not part: continue

                    match_pause = re.search(r"\[PAUSE:(\d+)\](.*)", part)
                    if match_pause:
                        manejar_pausa(match_pause.group(1), match_pause.group(2).strip())
                        continue 
                    
                    match_imagen = re.search(r"\[IMAGEN:\s*([^\]]+)\]", part)
                    if match_imagen:
                        text_before_tag = part[:match_imagen.start(0)].strip() if match_imagen.start(0) > 0 else ""
                        manejar_imagen(match_imagen.group(1).strip(), text_before_tag)
                        continue
                    
                    if re.search(r"\[TIEMPO\]", part):
                        sintetizar_tiempo()
                        continue
                    
                    match_ejercicio = re.search(r"\[EJERCICIO:\s*(\d+)\]", part)
                    if match_ejercicio:
                        manejar_ejercicio(match_ejercicio.group(1).strip())
                        continue
                    
                    speak(part)
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la ejecución: {e}")

if __name__ == "__main__":
    print("Iniciando el script de Pilates en Python...")
    print("--------------------------------------------------------------------")
    print("Nota: Este script utiliza comandos específicos de macOS ('say', 'open', 'afplay').")
    
    selected_pilates_file = None
    txt_files_in_dir = glob.glob("*.txt") # Busca archivos .txt para la rutina
    
    if not txt_files_in_dir:
        print("No se encontraron archivos .txt de Pilates en el directorio actual.")
    else:
        print("\nArchivos .txt de Pilates disponibles:")
        for i, filename in enumerate(txt_files_in_dir):
            print(f"  {i + 1}. {filename}")
        
        while True:
            try:
                choice_str = input(f"\nElige el número del archivo de Pilates a procesar (1-{len(txt_files_in_dir)}): ")
                choice_int = int(choice_str)
                if 1 <= choice_int <= len(txt_files_in_dir):
                    selected_pilates_file = txt_files_in_dir[choice_int - 1]
                    break
                else:
                    print(f"Selección inválida. Por favor, introduce un número entre 1 y {len(txt_files_in_dir)}.")
            except ValueError:
                print("Entrada inválida. Por favor, introduce un número.")
            except KeyboardInterrupt:
                print("\nSelección de archivo de Pilates cancelada. Saliendo.")
                selected_pilates_file = None
                break
        
    music_started_successfully = False
    if selected_pilates_file:
        print("--------------------------------------------------------------------")
        play_music_choice = input("¿Deseas añadir música de fondo? (s/N): ").strip().lower()
        music_file_to_play = None # Inicializar
        
        if play_music_choice == 's':
            print("\nInformación sobre la música de fondo:")
            print(" - Se usará 'afplay' de macOS, que reproducirá el archivo UNA SOLA VEZ.")
            print(" - Si deseas música continua, usa un archivo de audio largo.")

            # Listar archivos .mp3 en el directorio actual (case-insensitive para la extensión)
            all_files_in_cwd = os.listdir('.')
            mp3_files_in_dir = sorted([f for f in all_files_in_cwd if os.path.isfile(f) and f.lower().endswith('.mp3')])

            if not mp3_files_in_dir:
                print("\nNo se encontraron archivos .mp3 en el directorio actual.")
                music_file_to_play = input("Introduce la ruta completa a tu archivo de música (o deja vacío para omitir): ").strip()
                if not music_file_to_play: # Si se deja vacío
                    print("No se reproducirá música de fondo.")
            else:
                print("\nArchivos .mp3 disponibles para música de fondo:")
                for i, filename in enumerate(mp3_files_in_dir):
                    print(f"  {i + 1}. {filename}")
                print(f"  0. Omitir música / Introducir ruta manualmente")

                while True:
                    try:
                        mp3_choice_str = input(f"Elige el número del archivo .mp3 (1-{len(mp3_files_in_dir)}, o 0 para omitir/manual): ").strip()
                        mp3_choice_int = int(mp3_choice_str)

                        if 0 <= mp3_choice_int <= len(mp3_files_in_dir):
                            if mp3_choice_int == 0:
                                manual_path = input("Introduce la ruta completa a tu archivo de música (o deja vacío para omitir): ").strip()
                                music_file_to_play = manual_path if manual_path else None
                                if not music_file_to_play: print("No se reproducirá música de fondo.")
                            else:
                                music_file_to_play = mp3_files_in_dir[mp3_choice_int - 1]
                            break # Salir del bucle de selección de mp3
                        else:
                            print(f"Selección inválida. Introduce un número entre 0 y {len(mp3_files_in_dir)}.")
                    except ValueError:
                        print("Entrada inválida. Por favor, introduce un número.")
                    except KeyboardInterrupt:
                        print("\nSelección de música cancelada.")
                        music_file_to_play = None
                        break
            
            if music_file_to_play:
                music_started_successfully = start_background_music(music_file_to_play)
            # else: No es necesario un else aquí, music_file_to_play ya sería None o vacío
        
        main(selected_pilates_file) # Llama a la rutina principal de Pilates
    else:
        if not txt_files_in_dir:
            print("No hay archivos .txt para procesar. Saliendo.")
        # Mensaje de cancelación de archivo de Pilates ya mostrado si aplica

    if music_started_successfully:
         stop_background_music()

    print("--------------------------------------------------------------------")
    print("Script de Pilates finalizado.")