import os
import numpy as np
import sounddevice as sd
import time
import matplotlib.pyplot as plt
from datetime import datetime


DOCUMENTS_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")
FR_MEASUREMENTS_FOLDER = os.path.join(DOCUMENTS_FOLDER, "FR Measurements")

if not os.path.exists(FR_MEASUREMENTS_FOLDER):
    os.makedirs(FR_MEASUREMENTS_FOLDER)

FILENAME = f"response_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
OUTPUT_FILE = os.path.join(FR_MEASUREMENTS_FOLDER, FILENAME)

SAMPLE_RATE = 44100  
DURATION = 0.5      
FREQ_START = 20      
FREQ_END = 20000    
STEPS = 100         

REF_AMPLITUDE = 1.0  

def get_fr_measurements_folder():
    """Returns the path to the FR Measurements folder in Documents"""
    return os.path.join(os.path.expanduser("~"), "Documents", "FR Measurements")

def generate_sine_wave(frequency, duration, sample_rate):
    """Generates a sine wave of a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

def measure_response(frequency):
    """Plays a sine wave and records the microphone response in dB."""
    tone = generate_sine_wave(frequency, DURATION, SAMPLE_RATE)
    

    recording = sd.playrec(tone[:, np.newaxis], samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()  

    amplitude = np.abs(recording).mean()
    amplitude_dB = 20 * np.log10(max(amplitude, 1e-6) / REF_AMPLITUDE)  

    return amplitude_dB

def sine_sweep(output_file):
    """Performs a sine sweep and collects microphone response data in dB."""
    print("Starting frequency sweep from 20 Hz to 20 kHz...")
    
    frequencies = np.geomspace(FREQ_START, FREQ_END, STEPS)  
    response_data = []
    
    for freq in frequencies:
        print(f"Playing {freq:.2f} Hz...")
        amplitude_dB = measure_response(freq)
        response_data.append((freq, amplitude_dB))
        time.sleep(0.1)  
    
    print("Sweep complete. Saving response data...")
    save_to_txt(response_data, output_file)
    plot_response(response_data)

def save_to_txt(response_data, filename):
    """Saves the measured response data (in dB) to a text file in FR Measurements."""
    try:
        with open(filename, 'w') as file:
            for freq, amp_dB in response_data:
                file.write(f"{freq:.2f} {amp_dB:.2f}\n")  
        print(f"Response data saved to '{filename}'")
    except Exception as e:
        print(f"Error saving file: {e}")

def load_from_txt(file_name):
    """Loads frequency response data from a .txt file in the FR Measurements folder."""
    file_path = os.path.join(get_fr_measurements_folder(), file_name)
    
    response_data = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.replace(',', ' ').split()
                if len(parts) == 2:
                    try:
                        freq = float(parts[0])
                        amp_dB = float(parts[1])
                        response_data.append((freq, amp_dB))
                    except ValueError:
                        print(f"Skipping invalid line: {line.strip()}")
        
        if response_data:
            print("Data loaded successfully from file.")
            plot_response(response_data)
        else:
            print("No valid data found in file.")
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found in FR Measurements.")
    except Exception as e:
        print(f"Error reading file: {e}")

def plot_response(response_data):
    """Plots frequency response graph (with dB values), ensuring 15 dB gap from lowest value."""
    freqs, amplitudes_dB = zip(*response_data)

    min_dB = min(amplitudes_dB)  
    y_min = min_dB - 15  

    plt.figure(figsize=(8, 5))
    plt.plot(freqs, amplitudes_dB, marker='o', linestyle='-')
    plt.xscale('log')  
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude Response (dB)")
    plt.title("Frequency Response in dB")
    plt.ylim(y_min, max(amplitudes_dB) + 15)  
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.show()

def main():
    """User selects between running a sine sweep or loading a file from FR Measurements."""
    fr_folder = get_fr_measurements_folder()
    os.makedirs(fr_folder, exist_ok=True)
    
    print(f"\n📂 All files are saved to and loaded from: {fr_folder}")
    
    files = [f for f in os.listdir(fr_folder) if f.endswith('.txt')]
    
    if files:
        print("\nAvailable measurement files:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
    
    while True:
        choice = input("\nEnter 'sweep' to perform a sine sweep or choose a file number to load data: ").strip().lower()
        
        if choice == 'sweep':
            filename = f"response_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            output_file = os.path.join(fr_folder, filename)
            sine_sweep(output_file)
            break
        elif choice.isdigit():
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                load_from_txt(files[file_index])
                break
            print("Invalid selection. Please choose a valid file number.")
        else:
            print("Invalid input. Please enter 'sweep' or a valid file number.")

if __name__ == "__main__":
    main()