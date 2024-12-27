import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Function to read a CSV file
def read_waveform(file_path):
    data = pd.read_csv(file_path)
    time = data.iloc[:, 0].values * 1e9  # First column is time [ns]
    voltage = data.iloc[:, 1].values * 1e3  # Second column is voltage [mV]
    return time, voltage

# Function to extract rise time
def get_rise_time(time, voltage, threshold):
    cross_idx = np.argmax(voltage >= threshold)
    return time[cross_idx] if cross_idx > 0 else None

# Function to plot individual waveform using matplotlib
def plot_waveform(time, voltage, rise_time, threshold, save_path):
    plt.figure(figsize=(10, 6))
    plt.plot(time, voltage, marker='o', markersize=2, linestyle='-', label='Waveform')
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    if rise_time:
        plt.axvline(x=rise_time, color='g', linestyle='--', label='Rise Time')
    plt.title('Waveform')
    plt.xlabel('Time [ns]')
    plt.ylabel('Voltage [mV]')
    plt.legend()
    plt.savefig(save_path)
    plt.close()

# Function to plot the average waveform using matplotlib
def plot_average_waveform(time, avg_voltage, save_path):
    plt.figure(figsize=(10, 6))
    plt.grid()
    plt.plot(time, avg_voltage, marker='o', markersize=2, linestyle='-', label='Average Waveform')
    plt.xlabel('Time [ns]', fontsize=14, fontname='Times New Roman', loc='right')
    plt.ylabel('Voltage [mV]', fontsize=14, fontname='Times New Roman', loc='top')
    # x axis range
    plt.xlim(4.0, 5.0)
    plt.ylim(-1, 9)
    plt.savefig(save_path)
    plt.close()
    # calculate the rise time from 10% to 90%
    cross_idx_10 = np.argmax(avg_voltage >= 0.1 * avg_voltage.max())
    cross_idx_90 = np.argmax(avg_voltage >= 0.9 * avg_voltage.max())
    rise_time = time[cross_idx_90] - time[cross_idx_10]
    print(f"Average waveform rise time: {rise_time:.2f} ns")

# Main analysis function
def analyze_waveforms(folder_path, threshold, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    rise_times = [] 
    avg_voltage = None
    waveform_count = 0

    files = sorted(os.listdir(folder_path))  # Sort files to handle first 10 properly
    for i, file in enumerate(files):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            time, voltage = read_waveform(file_path)
            rise_time = get_rise_time(time, voltage, threshold)

            if rise_time:
                rise_times.append(rise_time)

            # Accumulate voltage for averaging
            if avg_voltage is None:
                avg_voltage = np.zeros_like(voltage)
                    
            avg_voltage += voltage
            waveform_count += 1

            # Plot the first 10 waveforms for checking
            if i < 10:
                plot_save_path = os.path.join(output_folder, f'waveform_{i+1}.pdf')
                plot_waveform(time, voltage, rise_time, threshold, plot_save_path)

    # Calculate the average waveform, its area in Q (50Ω) and plot it
    if waveform_count > 0:
        avg_voltage /= waveform_count
        avg_waveform_save_path = os.path.join(output_folder, 'average_waveform.pdf')
        plot_average_waveform(time, avg_voltage, avg_waveform_save_path)
        # area
        area = np.trapz(avg_voltage * 1e-3, time * 1e-9) / (50 * 1.62 * 1e-19) * 1e-6  # Convert to Qe
        print(f"Average waveform area: {area:.2f} Qe")
        # calculate the rise time from 10% to 90%
        cross_idx_10 = np.argmax(avg_voltage >= 0.1 * avg_voltage.max())
        cross_idx_90 = np.argmax(avg_voltage >= 0.9 * avg_voltage.max())
        rise_time = time[cross_idx_90] - time[cross_idx_10]
        print(f"Average waveform rise time: {rise_time:.2f} ns")
    
    # Plot and save histogram of rise times using matplotlib
    if rise_times:
        plt.figure(figsize=(10, 6))
        plt.hist(rise_times, bins=50, color='blue', alpha=0.7, label='Rise Times')
        plt.title('Histogram of Rise Times')
        plt.xlabel('TOA [ns]')
        plt.ylabel('Counts')
        plt.legend()
        hist_save_path = os.path.join(output_folder, 'rise_time_histogram.pdf')
        plt.savefig(hist_save_path)
        plt.close()

    print(f"Analysis complete. Output saved to: {output_folder}")

# Set your folder path, threshold, and output directory
folder_path = '/Users/lorenzo/cernbox/phd/Lab-measurements/FlexPCB-Aug24/24-10-28-waveforms-TPC-10ns-20mV-10pF/'  # Replace with your folder path
threshold = 2  # Threshold voltage for rise time detection [mV]
output_folder = '/Users/lorenzo/cernbox/phd/Lab-measurements/plots/TP-Connector/'  # Folder to save plots and results

# Run the analysis
analyze_waveforms(folder_path, threshold, output_folder)