import numpy as np
import scipy.optimize as opt
import scipy.interpolate as interp
import matplotlib.pyplot as plt
import os
from scipy.signal import medfilt

def get_fr_measurements_folder():
    """Returns the path to the FR Measurements folder in Documents"""
    return os.path.join(os.path.expanduser("~"), "Documents", "FR Measurements")

def list_measurement_files():
    """Lists available measurement files and returns selected file path"""
    fr_folder = get_fr_measurements_folder()
    if not os.path.exists(fr_folder):
        print(f"Error: FR Measurements folder not found at {fr_folder}")
        return None
    
    files = [f for f in os.listdir(fr_folder) if f.endswith('.txt')]
    if not files:
        print("No measurement files found in FR Measurements folder")
        return None
    
    print("\nAvailable measurement files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = input("\nSelect a file number (or 0 to cancel): ").strip()
            if choice == '0':
                return None
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                return os.path.join(fr_folder, files[file_index])
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def load_frequency_response(file_path):
    frequencies, amplitudes = np.loadtxt(file_path, unpack=True)
    return np.array(frequencies), np.array(amplitudes)

def harman_overear_target(frequencies):
    harman_freqs = np.array([20, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 8000, 10000, 12000, 16000, 20000])
    harman_levels = np.array([8, 7.2, 4.5, 0.5, 0, 0.5, 4.5, 8, 7, 4.5, 0.5, -2, -4, -6])
    interpolator = interp.interp1d(harman_freqs, harman_levels, kind='quadratic', fill_value='extrapolate')
    return interpolator(frequencies)

def match_amplitude_at_1khz(frequencies, amplitudes, target_func):
    measurement_1khz = np.interp(1000, frequencies, amplitudes)
    target_1khz = target_func(np.array([1000]))[0]
    offset = target_1khz - measurement_1khz
    return amplitudes + offset

def smooth_large_peaks(frequencies, response, kernel_size=7):
    if kernel_size % 2 == 0:
        kernel_size += 1
    smoothed = medfilt(response, kernel_size=kernel_size)
    return smoothed

def peaking_eq(f, f0, gain, q):
    return gain / (1 + ((f / f0 - f0 / f) ** 2) / (q ** 2))

def combined_filter(frequencies, params, num_peq_bands):
    eq_response = np.zeros_like(frequencies)
    
    for i in range(num_peq_bands):
        f0, gain, q = params[i * 3: (i + 1) * 3]
        eq_response += peaking_eq(frequencies, f0, gain, q)

    return eq_response

def frequency_weight(frequencies):
    """Weighting curve to prioritize all frequencies more evenly"""
    weights = np.ones_like(frequencies)

    log_freqs = np.log10(frequencies)
    min_log = np.log10(20)
    max_log = np.log10(15000)
    
    band_edges = np.logspace(min_log, max_log, num=11)
    for i in range(10):
        band_start = band_edges[i]
        band_end = band_edges[i+1]
        in_band = (frequencies >= band_start) & (frequencies <= band_end)
        weights[in_band] = 2.0 
    
    weights[frequencies < 20] = 0.1
    weights[frequencies > 15000] = 0.1
    
    return weights

def optimize_eq(frequencies, response, target, num_peq_bands=12):
    weights = frequency_weight(frequencies)
    
    def cost_function(params):
        eq_response = combined_filter(frequencies, params, num_peq_bands)
        error = (response + eq_response - target) * weights
        return np.sum(error ** 2) + 0.1 * np.sum(params[1::3] ** 2)

    min_freq = 20
    max_freq = 15000
    forced_freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), num_peq_bands)

    random_factor = 0.2 * (np.random.rand(num_peq_bands) - 0.1) 
    initial_freqs = forced_freqs * (1 + random_factor)
    
    initial_params = np.vstack([
        initial_freqs,
        np.zeros(num_peq_bands),
        np.full(num_peq_bands, 1.0)
    ]).flatten()


    bounds = []
    for i in range(num_peq_bands):
        band_min = forced_freqs[i] * 0.8 
        band_max = forced_freqs[i] * 1.2 
        bounds.extend([(band_min, band_max), (-12, 12), (0.5, 2.0)])


    print("Optimizing EQ parameters...")
    result = opt.minimize(cost_function, initial_params, bounds=bounds, 
                         method='Powell', options={'maxiter': 3000})
    refined = opt.minimize(cost_function, result.x, bounds=bounds,
                         method='L-BFGS-B', options={'maxiter': 1500})
    
    return refined.x

def main():
    input_file = list_measurement_files()
    if not input_file:
        return

    try:
        num_peq_bands = int(input("Enter the number of PEQ filters to use (default 10): ") or "10")
        if num_peq_bands < 1:
            print("Number of PEQ bands must be at least 1.")
            return
    except ValueError:
        print("Invalid input for number of filters. Please enter an integer.")
        return

    frequencies, response = load_frequency_response(input_file)

    valid_range = (frequencies >= 20) & (frequencies <= 15000)
    frequencies = frequencies[valid_range]
    response = response[valid_range]
    
    smoothed_response = smooth_large_peaks(frequencies, response)
    smoothed_response = match_amplitude_at_1khz(frequencies, smoothed_response, harman_overear_target)
    target = harman_overear_target(frequencies)

    optimized_params = optimize_eq(frequencies, smoothed_response, target, num_peq_bands)

    eq_lines = ["Preamp: -6 dB"]
    for i in range(num_peq_bands):
        f0, gain, q = optimized_params[i * 3: (i + 1) * 3]
        eq_lines.append(f"Filter: ON PK Fc {f0:.1f} Hz Gain {gain:.2f} dB Q {q:.2f}")

    eq_config = "\n".join(eq_lines)

    documents_folder = os.path.join(os.path.expanduser("~"), "Documents", "APO EQ")
    os.makedirs(documents_folder, exist_ok=True)
    output_file = os.path.join(documents_folder, "eq_apo_config.txt")

    with open(output_file, 'w') as f:
        f.write(eq_config)

    print(f"EqualizerAPO configuration saved to {output_file}")


    eq_response = combined_filter(frequencies, optimized_params, num_peq_bands)
    corrected_response = smoothed_response + eq_response
    max_deviation = np.max(np.abs(corrected_response - target))
    rms_error = np.sqrt(np.mean((corrected_response - target) ** 2))

    plt.figure(figsize=(14, 10))
    

    plt.subplot(2,1,1)
    plt.semilogx(frequencies, response, label='Original Response', alpha=0.5, color='gray')
    plt.semilogx(frequencies, smoothed_response, label='Smoothed Response', alpha=0.8, color='blue')
    plt.semilogx(frequencies, corrected_response, label='EQ Applied', linewidth=2, color='red')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.title('Frequency Response Comparison')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dB)')
    plt.xlim(20, 15000)
    

    plt.subplot(2,1,2)
    plt.semilogx(frequencies, target, label='Harman Target', linestyle='--', color='black')
    plt.semilogx(frequencies, corrected_response, label='After EQ', linewidth=1.5, color='red')
    plt.fill_between(frequencies, target-1.0, target+1.0, alpha=0.1, color='green', label='±1.0dB Tolerance')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.title(f'Equalization Result (Max Deviation: {max_deviation:.2f} dB, RMS Error: {rms_error:.2f} dB)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dB)')
    plt.xlim(20, 15000)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()