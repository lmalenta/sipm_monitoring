import os
import numpy as np
import pandas as pd
import ROOT

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

# Function to plot individual waveform using ROOT
def plot_waveform(time, voltage, rise_time, threshold, save_path):
    c = ROOT.TCanvas("c", "Waveform", 800, 600)
    graph = ROOT.TGraph(len(time), time, voltage)
    graph.SetTitle("Waveform")
    graph.GetXaxis().SetTitle("Time [ns]")
    graph.GetYaxis().SetTitle("Voltage [mV]")
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(0.2)
    graph.Draw("AP")

    # Draw threshold and rise time lines
    threshold_line = ROOT.TLine(time[0], threshold, time[-1], threshold)
    threshold_line.SetLineColor(ROOT.kRed)
    threshold_line.SetLineStyle(2)
    threshold_line.Draw("same")

    rise_time_line = ROOT.TLine(rise_time, voltage.min(), rise_time, voltage.max())
    rise_time_line.SetLineColor(ROOT.kGreen)
    rise_time_line.SetLineStyle(2)
    rise_time_line.Draw("same")

    c.SaveAs(save_path)
    del c

# Function to plot the average waveform using ROOT
def plot_average_waveform(time, avg_voltage, save_path):
    c_avg = ROOT.TCanvas("c_avg", "Average Waveform", 800, 600)
    graph_avg = ROOT.TGraph(len(time), time, avg_voltage)
    graph_avg.SetTitle("Average Waveform")
    graph_avg.GetXaxis().SetTitle("Time [ns]")
    graph_avg.GetYaxis().SetTitle("Voltage [mV]")
    graph_avg.SetMarkerStyle(20)
    graph_avg.SetMarkerSize(0.2)
    graph_avg.Draw("AP")
    c_avg.SaveAs(save_path)
    del c_avg

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
        #area
        area = np.trapz(avg_voltage * 1e-3, time * 1e-9) / ( 50 * 1.62 * 1e-19) * 1e-6  # Convert to Qe
        print(f"Average waveform area: {area:.2f} Qe")
    
    # Plot and save histogram of rise times using ROOT
    if rise_times:
        c_hist = ROOT.TCanvas("c_hist", "Rise Time Histogram", 800, 600)
        h = ROOT.TH1F("h", "Histogram of Rise Times;TOA (ns);", 200, 4.2, 4.6) 
        ROOT.gStyle.SetOptStat(0)
        for rt in rise_times:
            h.Fill(rt)

        # Fit a Gaussian to the histogram
        fit = ROOT.TF1("gauss_fit", "gaus", 4.2, 4.6)
        fit.SetNpx(1000)
        h.Fit("gauss_fit", "R")
        h.Draw()
        fit.Draw("same")

        hist_save_path = os.path.join(output_folder, 'rise_time_histogram.pdf')
        c_hist.SaveAs(hist_save_path)
        del c_hist
        del h
        del fit

    print(f"Analysis complete. Output saved to: {output_folder}")

# Set your folder path, threshold, and output directory
folder_path = '/Users/lorenzo/cernbox/phd/Lab-measurements/FlexPCB-Aug24/24-10-28-waveforms-TPC-10ns-20mV-10pF/'  # Replace with your folder path
threshold = 2  # Threshold voltage for rise time detection [mV]
output_folder = '/Users/lorenzo/cernbox/phd/Lab-measurements/plots/TP-Connector/'  # Folder to save plots and results

# Run the analysis
analyze_waveforms(folder_path, threshold, output_folder)
