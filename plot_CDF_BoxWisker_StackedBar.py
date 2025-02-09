# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                               <<< SOME NOTES >>>                              #
#                                                                               #
#>>> This script uses pickled atmospheric model output data to draw the         #
#    cumulative distribution function (CDF) plot, box-whisker plot, and         #
#    stacked-bar chart.                                                         #
#                                                                               #
#>>> The script could handle multiple input files, each one containing multiple #
#    variables, in a single execution.                                          #
#                                                                               #
#>>> The input pickled data could be grided (2D) or non-gridded time series     #
#    (1D).                                                                      #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

"""
@author : Reza Rezaei
email   : rezarezaei2008@gmail.com
version : 1.0
year    : 2023
"""

import os
import math 
import shutil
import pprint
import matplotlib
import numpy as np
import _pickle as cPickle
import matplotlib.pyplot as plt



class Plot():
    def __init__(self, input_pkls, output_dir):
        self.in_pkls = input_pkls
        self.outdir = output_dir
        print(f"\nPlots will be saved in:\n {self.outdir}")
        
    def append2Dict(self):
        var_dict = {}
        for pkl in self.in_pkls:
            with open(pkl, "rb") as fp:
                pkld_dt = cPickle.load(fp)
                year = pkld_dt["Year"]
                scenario = pkld_dt["Scenario Name"]
                cur_pkl_key = f"{str(year)} ({scenario})"
                                
                for key, value in pkld_dt.items():
                    if type(value) == dict:
                        data_arr_list = []                
                        if key not in var_dict.keys():
                            var_dict[key] = {}
                        var_dict[key][cur_pkl_key] = None
                        for month, data_dict in value.items():
                            for day, vals in data_dict.items():
                                if len(vals.shape) == 2:
                                    vals = vals.reshape(vals.shape[0]*vals.shape[1])    
                                data_arr_list.append(vals)
                
                        data_arr = np.array(data_arr_list)
                        if len(data_arr.shape) == 2:
                            data_arr = data_arr.reshape(data_arr.shape[0]*data_arr.shape[1]) 
                        var_dict[key][cur_pkl_key] = data_arr
                        var_dict[f"{key}_unit"] = pkld_dt[f"{key}_unit"]
            
            var_dict["Year"] = year
            var_dict["Scenario Name"] = scenario
            var_dict["Model"] = pkld_dt["Model"]
            var_dict["Domain Name"] = pkld_dt["Domain Name"]
            var_dict["Data Period"] = pkld_dt["Data Period"]                  
            var_dict["Data Type"] = pkld_dt["Data Type"]                     
            var_dict["Statistical Measure"] = pkld_dt["Statistical Measure"]  
        return var_dict
    
    def CDF(self):       
        """Cumulative Distribution Function plot"""
        var_dict = self.append2Dict()
        
        for param, value in var_dict.items():
            if type(value) == dict:            
                fig, ax = plt.subplots(figsize=(12,10))
                for scenario, data in value.items():
                    y_values = np.arange(len(data)) / float(len(data))
                    x_values = np.sort(data)                          
                    param_unit = var_dict[f"{param}_unit"]           
                    ax.plot(x_values, y_values, label=scenario, linestyle="", 
                            marker=".", markersize=12)
                plt.grid(color="grey", linestyle="--")     
                plt.tick_params(axis='both', which='major', labelsize=30)   
                plt.xticks(rotation=0)
                plt.xlabel(f"{param} ({param_unit})" , fontsize=40)
                plt.ylabel("Cumulative Proportion", fontsize=40)
                                    
                file_name = "CDF-plot_{0}-domain_{1}-output_{2}-{3}-{4}_{5}.png".format(
                        var_dict["Domain Name"], var_dict["Model"], 
                        var_dict["Data Type"], str(var_dict["Data Period"]).lower(),
                        str(var_dict["Statistical Measure"]).lower(), param)
                    
                file = os.path.join(self.outdir, file_name)
                plt.savefig(file, dpi=300, bbox_inches='tight')
                plt.close()
    
    def BoxWhisker(self, tufte_style, single_color):   
        """Box-Whisker plot"""
        var_dict = self.append2Dict()
        
        for param, value in var_dict.items():
            if type(value) == dict:      
                fig, ax = plt.subplots(figsize=(5.0,2.8))

                values = []
                scenarios = []
                for scenario, data in value.items():
                    scenarios.append(scenario)
                    x_values = np.sort(data)
                    param_unit = var_dict[f"{param}_unit"]
                    values.append(x_values)
                
                meanprops = dict(markerfacecolor="green", marker="D", markeredgecolor="green")
                medianprops = dict(color="black", linewidth=1.5)
                flierprops = dict(marker="o", markerfacecolor="white", markersize=4,
                                  linestyle='none', markeredgecolor="black")
                scenario_list = [scenario.replace(" ","\n") for scenario in scenarios]
                boxplot = plt.boxplot(values, labels=scenario_list, vert=False,   
                            showmeans=False, meanprops=meanprops, notch=True, 
                            medianprops=medianprops, showfliers=True, 
                            flierprops=flierprops, patch_artist=True)
                
                if single_color == True:
                    for box in boxplot['boxes']:
                        box.set(facecolor = "#3D1C02" )
                elif single_color == False:
                    clrs = ["blue", "darkorange", "green", "#00FFFF", "#BBF90F",
                            "#C1F80A", "#0000FF", "#006400", "#FFD700", "#DAA520"]
                    for patch, color in zip(boxplot['boxes'], clrs):
                        patch.set_facecolor(color)
                
                if tufte_style == True:
                    ax.spines.right.set_visible(False)
                    ax.spines.top.set_visible(False)
                    ax.spines['bottom'].set_bounds(round(np.nanmin(values, axis=(0,1))), 
                                                   round(np.nanmax(values, axis=(0,1))))
                    ax.spines['left'].set_bounds(math.ceil(ax.get_ylim()[0]), 
                                                 math.floor(ax.get_ylim()[1]))
                    x_ticks = list(range(int(np.nanmin(values, axis=(0,1))), 
                                         int(np.nanmax(values, axis=(0,1)))+1, 2))
                    ax.xaxis.set_ticks(x_ticks)
                    ax.set_xlim([ax.get_xlim()[0], ax.get_xlim()[1]])
                    ax.set_ylim([ax.get_ylim()[0], ax.get_ylim()[1]])
                                        
                plt.tick_params(axis="both", which="major", labelsize=12)      
                plt.yticks(rotation=0)                
                stat = var_dict["Statistical Measure"]
                plt.xlabel(f"{stat} {param} ({param_unit})", fontsize=14)      
                plt.ylabel("Scenario", fontsize=14)
                plt.title(var_dict["Domain Name"], fontsize=15)
                
                file_name = "Box-plot_{0}-domain_{1}-output_{2}-{3}-{4}_{5}.png".format(
                        var_dict["Domain Name"], var_dict["Model"], 
                        var_dict["Data Type"], str(var_dict["Data Period"]).lower(),
                        str(var_dict["Statistical Measure"]).lower(), param)
                    
                file = os.path.join(self.outdir, file_name)
                plt.savefig(file, dpi=300, bbox_inches='tight')
                plt.close()      

    def stackedBarChart(self):
        """stacked-Bar Chart"""
        var_dict = self.append2Dict()
        
        df_dict = {}
        for param, value in var_dict.items():
            if type(value) == dict:
                df_dict[param] = {}
                for scenario, data in value.items():
                    total_per_tonne = round(np.sum(data), 2)
                    df_dict[param][scenario] = total_per_tonne
                
        scenario_list = list(df_dict[list(df_dict.keys())[0]].keys())
        scenario_list = [scen.split(" ")[1][1:-1] for scen in scenario_list]  
        
        data_dict = {key:[] for key in scenario_list}
        for param, scenarios in df_dict.items():
            for scenario, data in scenarios.items():
                cur_scen = scenario.split(" ")[1][1:-1]
                data_dict[cur_scen].append(data)
        
        fig, ax = plt.subplots(figsize=(8,4))
        ind = np.arange(len(df_dict.keys()))
        
        lgnd_item = []
        bottom = None
        for count, val in enumerate(scenario_list):
            if count == 0:
                plot = plt.bar(ind, data_dict[val], width=0.45)
                lgnd_item.append(plot[0])
            else:
                plot = plt.bar(ind, data_dict[val], bottom=bottom, width=0.45)
                lgnd_item.append(plot[0])
            bottom = data_dict[val]
        
        ax.set_yscale("log")        
        plt.xticks(ind, tuple(df_dict.keys()), rotation=45) 
        plt.legend(tuple(lgnd_item), tuple(scenario_list), fontsize=10)
        plt.xlabel("Species", fontsize=15)
        plt.ylabel("Tonne", fontsize=15)
        
        scen_list = " ".join(scenario_list).replace(" ", "_")
        
        file_name = "stacked-bar-plot_{0}-scenarios.png".format(scen_list)
        file = os.path.join(self.outdir, file_name)
        plt.savefig(file, dpi=300, bbox_inches='tight')
        plt.close()
        print("\nThe output file is saved as:\n"\
              f"{file}")


         

#===================================== RUN ====================================

"""
# BoxWhisker and CDF plots
pkl_list=[
    "C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2012/pickled_daily-timeseries-mean-values_Marmara-domain_MCIP-outputs_2012_past-scenario_TEMP2_PBL_WSPD10.pkl",
    "C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2053_ssp245/pickled_daily-timeseries-mean-values_Marmara-domain_MCIP-outputs_2053_ssp2-4.5-scenario_TEMP2_PBL_WSPD10.pkl",
    "C:/Users/Reza/Desktop/pickle_cctm_outs/MCIP/2053_ssp585/pickled_daily-timeseries-mean-values_Marmara-domain_MCIP-outputs_2053_ssp5-8.5-scenario_TEMP2_PBL_WSPD10.pkl"
         ]
"""

# stacked bar plot
pkl_list=[
    "F:/emiss_eproc_outputs/4km/marmara/pickled_monthly-gridded-total-values_Marmara-domain_EPROC-outputs_2012_anthropogenic-scenario_ISOP_TERP_AACD_ACET_ALD2_ETH_ETOH_FACD_FORM_IOLE_MEOH_OLE_BENZ_CO_CH4_NOx.pkl",
    "C:/Users/Reza/Desktop/pickle_cctm_outs/MEGAN/2012/pickled_monthly-gridded-total-values_Marmara-domain_MEGAN-outputs_2012_biogenic-scenario_ISOP_TERP_AACD_ACET_ALD2_ETH_ETOH_FACD_FORM_IOLE_MEOH_OLE_BENZ_CO_CH4_NOx.pkl"
        ]



ins = Plot(input_pkls=pkl_list, 
           output_dir="C:/Users/Reza/Desktop/pickle_cctm_outs/")

#ins.CDF()
#ins.BoxWhisker(tufte_style=True, single_color=False)
ins.stackedBarChart()