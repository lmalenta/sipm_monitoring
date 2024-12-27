####################################################################################################
#
#
# This script generates I-V curves for the SiPM Flex-PCB testing. 
#
#
####################################################################################################


import numpy as np
import ROOT


# Load the LHCb style (if needed)
ROOT.gROOT.ProcessLine('.L lhcbstyle.C')





# Voltages
voltages = np.array([50.0, 50.5, 51.0, 51.5, 52.0, 52.5, 53.0, 53.5, 54.0, 54.5, 55.0, 55.5, 56.0, 56.5, 57.0, 57.5, 58.0])

# Currents for firts half of the SiPM (RC filters on)
currents_1 = np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.40, 1.20, 2.20, 3.35, 4.85, 6.60, 8.75, 11.60, 15.45])

# Currents for second half of the SiPM (RC filters off)
currents_2 = np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.40, 1.20, 2.10, 3.25, 4.60, 6.25, 8.35, 11.20, 14.75])

# Currents for the whole SiPM
currents_3 = np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.30, 1.30, 2.65, 4.25, 6.25, 8.50, 11.40, 14.95, 19.40, 25.50, 33.15])

# Plot the I-V curves in the sme graph with different colors
c = ROOT.TCanvas("c", "I-V Curves", 800, 600)
# c.SetGrid()

graph_1 = ROOT.TGraph(len(voltages), voltages, currents_1)
# log scale y
c.SetLogy()
graph_1.SetTitle("I-V Curves")
graph_1.GetXaxis().SetTitle("Voltage [V]")
graph_1.GetYaxis().SetTitle("Current [#muA]")
graph_1.SetMarkerStyle(20)
graph_1.SetMarkerSize(0.8)
graph_1.SetMarkerColor(ROOT.kRed)
graph_1.SetLineColor(ROOT.kRed)
graph_1.GetYaxis().SetRangeUser(0, 40)
graph_1.Draw("ALP")

graph_2 = ROOT.TGraph(len(voltages), voltages, currents_2)
graph_2.SetMarkerStyle(20)
graph_2.SetMarkerSize(0.8)
graph_2.SetMarkerColor(ROOT.kBlue)
graph_2.SetLineColor(ROOT.kBlue)
graph_2.Draw("LP")

graph_3 = ROOT.TGraph(len(voltages), voltages, currents_3)
graph_3.SetMarkerStyle(20)
graph_3.SetMarkerSize(0.8)
graph_3.SetMarkerColor(ROOT.kGreen)
graph_3.SetLineColor(ROOT.kGreen)
graph_3.Draw("LP")

legend = ROOT.TLegend(0.2, 0.7, 0.5, 0.9)
legend.AddEntry(graph_1, "RC Filters half", "p")
legend.AddEntry(graph_2, "No filters half", "p")
legend.AddEntry(graph_3, "Full SiPM", "p")

legend.Draw()
c.SaveAs("/Users/lorenzo/cernbox/phd/Lab-measurements/plots/iv-curves/iv-curves-flex-pcb.pdf")

del c