# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                               <<< SOME NOTES >>>                              #
#                                                                               #
#>>> This script uses pickled WRF outputs to draw wind rose plots.              #  
#                                                                               #
#>>> The script can process multiple input pickle files in single run.          #
#                                                                               #
#>>> To draw multiple wind rose plots with similar bins in the legend, the      #
#    argument named 'bins' must be set. If the argument is left empty (""),     #
#    each plot will have different bins.                                        #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

"""
@author : Reza Rezaei
email   : rezarezaei2008@gmail.com
version : 1.0
year    : 2023
"""

import os
import numpy as np
import _pickle as cPickle
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from matplotlib.pyplot import figure

# pip install windrose

class WindRose:
    def __init__(self, input_pkls, output_dir, sub_period_plot, bins=""):
        self.pkls = input_pkls
        self.outdir = output_dir
        self.subplt = sub_period_plot
        self.bins = bins
    
    def getData(self, pkl_data, parameter):
        dt_file = open(pkl_data, "rb")
        data = cPickle.load(dt_file)
        
        year = data["Year"]
        scenario = data["Scenario Name"]
        dom_name = data["Domain Name"]
        unit = data[f"{parameter}_unit"]
        
        reshaped_data = {}
        for month in data[parameter].keys():
            reshaped_data[month] = {}
            
            if self.subplt == True:
                for period in data[parameter][month].keys():
                    reshaped_data[month][period] = None
                    vals = data[parameter][month][period]   
                    reshaped_vals = vals.reshape(
                                vals.shape[0]*vals.shape[1]*vals.shape[2])
                    reshaped_data[month][period] = reshaped_vals
            elif self.subplt == False:
                arr = []
                reshaped_data[month]["dt"] = None
                for period in data[parameter][month].keys():  
                    reshaped_data[month]
                    vals = data[parameter][month][period]
                    reshaped_vals = vals.reshape(
                                vals.shape[0]*vals.shape[1]*vals.shape[2])
                    arr.append(reshaped_vals)
                
                data_arr = np.array(arr)
                data_arr = data_arr.reshape(data_arr.shape[0]*data_arr.shape[1])
                reshaped_data[month]["dt"] = data_arr

        return year, scenario, dom_name, unit, reshaped_data

    def drawWindRose(self):  
        for pkl in self.pkls:          
            year, scenario, dom_name, wdir_unit, wdir_data = \
                self.getData(pkl, "WDIR10")    
            
            _, _, _, wspd_unit, wspd_data = \
                self.getData(pkl, "WSPD10")     
            
            for period, sub_period in wdir_data.items():
                for key, data in sub_period.items():
                    wdir_dt = wdir_data[period][key]
                    wspd_dt = wspd_data[period][key]
                                    
                    plt.rcParams["figure.figsize"] = (7,6)
                    ax = WindroseAxes.from_ax()
                    if self.bins:
                        a, b, c = self.bins[0], self.bins[1], self.bins[2]
                        ax.bar(wdir_dt, wspd_dt, normed=True, opening=0.8, edgecolor="white",
                               bins=np.arange(a, b, c))  
                    else:
                        ax.bar(wspd_dt, wspd_dt, normed=True, opening=0.8, edgecolor="white")
                    
                    if key == "dt":
                        sub_name = ""
                    else:
                        sub_name = key
                    ttl = f"{dom_name} - {year} ({scenario}) \n {period} {sub_name}"
                    ax.set_title(ttl , fontdict={'fontsize': 24})
                                                  
                    xlabels = [i.get_text() for i in ax.get_xticklabels()]
                    ax.set_xticklabels(xlabels, fontsize = 18, fontweight="bold")
                    ylabels = [j.get_text() for j in ax.get_yticklabels()]
                    ax.set_yticklabels(ylabels, fontsize = 18)  
                    ax.set_legend(fontsize=22)
                            
                    file_name = f"windrose-plot_{year}-{scenario}-scenario_{dom_name}_{period}-{sub_name}.png"
                    file = os.path.join(self.outdir, file_name)
                    plt.savefig(file, dpi=300, bbox_inches="tight")




#===================================== RUN ====================================
pkls = ["C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2012/pickled_seasonal-gridded-data-Marmara-domain_MCIP-outputs_2012_reference-scenario_WSPD10_WDIR10.pkl",
        "C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2053_ssp245/pickled_seasonal-gridded-data-Marmara-domain_MCIP-outputs_2053_ssp2-4.5-scenario_WSPD10_WDIR10.pkl",
        "C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2053_ssp585/pickled_seasonal-gridded-data-Marmara-domain_MCIP-outputs_2053_ssp5-8.5-scenario_WSPD10_WDIR10.pkl"
        ]

ins = WindRose(
    input_pkls=pkls,
    output_dir="C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP",
    sub_period_plot =True,   # if 'True': draws separate plot for each sub-period (each month, daytime/nighttime, daily time slices)
                             # if 'False': draw single plot for each input pickle file
    bins=[0, 18, 4])         # bins=[start, stop, step]  or  bins=""

ins.drawWindRose()
