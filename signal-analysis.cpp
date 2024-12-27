#include <TCanvas.h>
#include <TGraph.h>
#include <TH1F.h>
#include <TF1.h>
#include <TLine.h>
#include <TStyle.h>
#include <TLegend.h>
#include <TMath.h>
#include <TRandom.h>
#include <TSystem.h>
#include <TString.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <numeric>
#include <sstream>
#include <TROOT.h>



// Function to read a CSV file and populate time and voltage vectors
void read_waveform(const std::string &file_path, std::vector<double> &time, std::vector<double> &voltage) {
    std::ifstream infile(file_path);
    std::string line;
    while (std::getline(infile, line)) {
        std::stringstream ss(line);
        double t, v;
        char comma;
        ss >> t >> comma >> v;
        time.push_back(t * 1e9);    // Convert time to ns
        voltage.push_back(v * 1e3); // Convert voltage to mV
    }
}

// Function to find the rise time based on a voltage threshold
double get_rise_time(const std::vector<double> &time, const std::vector<double> &voltage, double threshold) {
    for (size_t i = 0; i < voltage.size(); ++i) {
        if (voltage[i] >= threshold) {
            return time[i];
        }
    }
    return -1.0; // Return -1 if threshold is not crossed
}

// Function to plot a single waveform
void plot_waveform(const std::vector<double> &time, const std::vector<double> &voltage, double rise_time, double threshold, const std::string &save_path) {
    TCanvas c("c", "Waveform", 800, 600);
    TGraph graph(time.size(), &time[0], &voltage[0]);
    graph.SetTitle("Waveform;Time [ns];Voltage [mV]");
    graph.SetMarkerStyle(20);
    graph.SetMarkerSize(0.5);
    graph.Draw("AP");

    TLine threshold_line(time.front(), threshold, time.back(), threshold);
    threshold_line.SetLineColor(kRed);
    threshold_line.SetLineStyle(2);
    threshold_line.Draw();

    if (rise_time > 0) {
        TLine rise_time_line(rise_time, *std::min_element(voltage.begin(), voltage.end()), rise_time, *std::max_element(voltage.begin(), voltage.end()));
        rise_time_line.SetLineColor(kGreen);
        rise_time_line.SetLineStyle(2);
        rise_time_line.Draw();
    }

    c.SaveAs(save_path.c_str());
}

void plot_average_waveform(const std::vector<double>& time, const std::vector<double>& avg_voltage, const std::string& save_path) {
    // Create a new canvas for the plot
    TCanvas* c_avg = new TCanvas("c_avg", "Average Waveform", 800, 600);
    
    // Create a TGraph from the time and voltage vectors
    TGraph* graph_avg = new TGraph(time.size(), &time[0], &avg_voltage[0]);
    
    // Set title and axis labels
    graph_avg->SetTitle("Average Waveform");
    graph_avg->GetXaxis()->SetTitle("Time [ns]");
    graph_avg->GetYaxis()->SetTitle("Voltage [mV]");
    
    // Set marker style and size
    graph_avg->SetMarkerStyle(20);  // Circle markers
    graph_avg->SetMarkerSize(0.2);  // Marker size
    
    // Draw the graph
    graph_avg->Draw("AP");
    
    // Save the plot to the specified file
    c_avg->SaveAs(save_path.c_str());
    
    // Clean up
    delete c_avg;
    delete graph_avg;
}

// Main function for analyzing waveforms
void analyze_waveforms(const std::string &folder_path, double threshold, const std::string &output_folder) {

    std::vector<double> rise_times;
    std::vector<double> avg_voltage;
    size_t waveform_count = 0;

    void *dir = gSystem->OpenDirectory(folder_path.c_str());
    const char *entry;
    while ((entry = gSystem->GetDirEntry(dir))) {
        std::string file_name(entry);
        if (file_name.find(".csv") != std::string::npos) {
            std::vector<double> time, voltage;
            read_waveform(folder_path + "/" + file_name, time, voltage);
            double rise_time = get_rise_time(time, voltage, threshold);

            if (rise_time > 0) {
                rise_times.push_back(rise_time);
            }

            if (avg_voltage.empty()) {
                avg_voltage.resize(voltage.size(), 0.0);
            }

            for (size_t i = 0; i < voltage.size(); ++i) {
                avg_voltage[i] += voltage[i];
            }

            waveform_count++;
            if (waveform_count <= 10) {
                plot_waveform(time, voltage, rise_time, threshold, output_folder + "/waveform_" + std::to_string(waveform_count) + ".pdf");
            }
        }
    }

    if (waveform_count > 0) {
        for (auto &v : avg_voltage) v /= waveform_count;

        std::vector<double> time(avg_voltage.size());
        std::iota(time.begin(), time.end(), 0);  // Assuming uniform time step
        plot_average_waveform(time, avg_voltage, output_folder + "/average_waveform.pdf");

    }

    if (!rise_times.empty()) {
        TCanvas c_hist("c_hist", "Rise Time Histogram", 800, 600);
        double min_rt = *std::min_element(rise_times.begin(), rise_times.end());
        double max_rt = *std::max_element(rise_times.begin(), rise_times.end());

        TH1F h("h", "Histogram of Rise Times;TOA [ns];Counts", 100, min_rt, max_rt);
        for (double rt : rise_times) {
            h.Fill(rt);
        }

        TF1 gauss_fit("gauss_fit", "gaus", min_rt, max_rt);
        h.Fit("gauss_fit", "R");
        h.Draw();
        c_hist.SaveAs((output_folder + "/rise_time_histogram.pdf").c_str());
    }
}

int main() {
    gROOT->ProcessLine(".L  lhcbstyle.C");
    std::string folder_path = "/Users/lorenzo/cernbox/phd/Lab-measurements/FlexPCB-Aug24/24-10-28-waveforms-TPC-10ns-20mV-10pF/";  // Set this to your folder path
    double threshold = 2.0;  // Set your threshold in mV
    std::string output_folder = "/Users/lorenzo/cernbox/phd/Lab-measurements/plots/TP-Connector/";  // Set this to your output folder

    analyze_waveforms(folder_path, threshold, output_folder);
    return 0;
}