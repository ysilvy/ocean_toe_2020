#!/bin/env python
# -*- coding: utf-8 -*-

"""
Python matplotlib
Make whisker plots of ToE hist+RCP85 vs. histNat (or Picontrol) in all 5 domains, with x axis being the GSAT anomaly
>1std and >2std
"""
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from netCDF4 import Dataset as open_ncfile
from maps_matplot_lib import defVarmme
from modelsDef import defModels, defModelsCO2piC
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import glob
import os
import datetime
from functions_ToE import read_toe_rcp85, read_gsat_rcp85, read_toe_1pctCO2, read_gsat_1pctCO2


# ----- Work -----

# Directory
indir_rcphn = '/home/ysilvy/Density_bining/Yona_analysis/data/toe_rcp85_histNat_average_signal/'
indir_rcppiC = '/home/ysilvy/Density_bining/Yona_analysis/data/toe_rcp85_PiControl_average_signal/'
indir_CO2piC = '/home/ysilvy/Density_bining/Yona_analysis/data/toe_1pctCO2vsPiC_average_signal/'
indir_gsat = '/home/ysilvy/Density_bining/Yona_analysis/data/gsat/'

models = defModels()
modelsCO2 = defModelsCO2piC()

domains = ['Southern ST', 'SO', 'Northern ST', 'North Atlantic', 'North Pacific']

varname = defVarmme('salinity'); v = 'S'

method = 'average_signal' # Average signal and noise in the box, then compute ToE
method_noise_histNat = 'average_histNat' # Average histNat (or PiControl) in the specified domains then determine the std of this averaged value
method_noise_piC = 'average_piC'

# === INPUTS ===

# -- Choose 2 datasets to plot/compare on the figure
# work = 'rcp85_histNat_1_2std' # Supplementary figure 10
# work = 'rcp85_histNat_PiControl_2std' # Supplementary figure 11
work = 'rcp85_histNat_1pctCO2_2std' #Supplementary figure 8

# output format
# outfmt = 'view'
outfmt = 'save'

# ===========

# ----- Variables ------
var = varname['var_zonal_w/bowl']
legVar = varname['legVar']
unit = varname['unit']

timN = 240

degree_sign= u'\N{DEGREE SIGN}'

# ------ Define directories, plot names, etc.. according to work -----

if work == 'rcp85_histNat_1_2std':
    indir1 = indir_rcphn
    indir2 = indir_rcphn
    varread1 = var+'ToE2'
    varread2 = var+'ToE1'
    ignore1 = [] # Models to ignore for some reason
    ignore2 = []
    color = '#e47f8a' # Color boxes for 2nd set of data
    title1 = 'Hist + RCP8.5 vs. histNat [>2std]'
    title2 = 'Hist + RCP8.5 vs. histNat [>1std]'
    plotName = 'GSATatE_boxplot_' + work +'_'+method_noise_histNat
elif work == 'rcp85_histNat_PiControl_2std':
    indir1 = indir_rcphn
    indir2 = indir_rcppiC
    varread1 = var+'ToE2'
    varread2 = var+'ToE2'
    ignore1 = ['GISS-E2-R','FGOALS-g2','MIROC-ESM']
    ignore2 = ['GISS-E2-R','FGOALS-g2','MIROC-ESM']
    color = '#3D8383'
    title1 = 'Hist + RCP8.5 vs. histNat [>2std]'
    title2 = 'Hist + RCP8.5 vs. PiControl [>2std]'
    plotName = 'GSATatE_boxplot_' + work +'_'+method_noise_histNat+'_'+method_noise_piC
else:
    indir1 = indir_rcphn
    indir2 = indir_CO2piC
    varread1 = var+'ToE2'
    varread2 = var+'ToE2'
    ignore1 = []
    ignore2 = []
    color = '#004f82'
    title1 = 'Hist + RCP8.5 vs. histNat [>2std]'
    title2 = '1pctCO2 vs. PiControl [>2std]'
    plotName = 'GSATatE_boxplot_' + work +'_'+method_noise_histNat+'_'+method_noise_piC

# ----- Read ToE and tas for each model ------

listfiles1 = sorted(glob.glob(indir1 + method_noise_histNat + '/*'+legVar+'_toe_rcp_histNat*.nc'))
nmodels1 = len(listfiles1)-len(ignore1)

if work != 'rcp85_histNat_1_2std':
    listfiles2 = sorted(glob.glob(indir2 + method_noise_piC + '/*.nc'))
    nmodels2=len(listfiles2)
else:
    listfiles2 = listfiles1
    nmodels2 = len(listfiles2)-len(ignore2)


# Read ToE
varToEA_1, varToEP_1, varToEI_1, nMembers1 = read_toe_rcp85(varread1,listfiles1,ignore1,len(domains))
if work != 'rcp85_histNat_1pctCO2_2std':
    varToEA_2, varToEP_2, varToEI_2, nMembers2 = read_toe_rcp85(varread2,listfiles2,ignore2,len(domains))
else:
    varToEA_2, varToEP_2, varToEI_2, nMembers2 = read_toe_1pctCO2(varread2, indir2+'average_piC',modelsCO2,ignore2,len(domains))
    nmodels2 = nmodels2-len(ignore2)

# Read GSAT
gsat_anom1 = read_gsat_rcp85(indir_gsat+'hist-rcp85/',listfiles1,ignore1)
if work != 'rcp85_histNat_1pctCO2_2std':
    gsat_anom2 = gsat_anom1
else:
    gsat_anom2 = read_gsat_1pctCO2(indir_gsat,modelsCO2,ignore2) # Anomaly relative to the last 100 years of piControl

nruns1 = np.sum(nMembers1)
nruns1 = int(nruns1)
nruns2 = int(np.sum(nMembers2))

# Smooth gsat anomaly time series
da_gsat_anom1 = xr.DataArray(gsat_anom1, dims=('time','members'))
da_gsat_anom2 = xr.DataArray(gsat_anom2, dims=('time','members'))
gsat_anom1_smooth = da_gsat_anom1.rolling(time=10,center=True,min_periods=1).mean()
gsat_anom2_smooth = da_gsat_anom2.rolling(time=10,center=True,min_periods=1).mean()

# ---- Associate ToE to GSAT anomaly ----

maskdata  = np.nan
time1 = np.arange(1861,2101)
if work == 'rcp85_histNat_1pctCO2_2std':
    time2 = np.arange(1,141)
else:
    time2 = time1

# Make new data associating each ToE to its corresponding temperature anomaly
def associate_gsat_ToE(varToE,time,gsat_anom):
    """ Make new data array associating each ToE to its corresponding temperature anomaly """
    ndomains = varToE.shape[1]
    nruns = varToE.shape[0]
    varToE_gsat = np.ma.empty((nruns,ndomains))

    for idomain in range(ndomains): # Loop on regions
        for irun in range(nruns): # Loop on all realizations
            toe = varToE[irun,idomain] # Read ToE
            if not np.ma.is_masked(toe):
                iyear = np.argwhere(time==toe)[0][0] # Read index of said ToE in time vector
                varToE_gsat[irun,idomain] = gsat_anom[iyear,irun] # Fill new data array with gsat anomaly
            else:
                varToE_gsat[irun,idomain] = np.ma.masked

    return varToE_gsat

varToEA_1_gsat = associate_gsat_ToE(varToEA_1,time1,gsat_anom1_smooth)
varToEP_1_gsat = associate_gsat_ToE(varToEP_1,time1,gsat_anom1_smooth)
varToEI_1_gsat = associate_gsat_ToE(varToEI_1,time1,gsat_anom1_smooth)
varToEA_2_gsat = associate_gsat_ToE(varToEA_2,time2,gsat_anom2_smooth)
varToEP_2_gsat = associate_gsat_ToE(varToEP_2,time2,gsat_anom2_smooth)
varToEI_2_gsat = associate_gsat_ToE(varToEI_2,time2,gsat_anom2_smooth)

# -- Median of members
nruns=0
medvarToEA_1_gsat = np.ma.masked_all((nmodels1,len(domains)))
medvarToEP_1_gsat = np.ma.masked_all((nmodels1,len(domains)))
medvarToEI_1_gsat = np.ma.masked_all((nmodels1,len(domains)))
nMembers1_non0 = nMembers1[np.ma.nonzero(nMembers1)]
for i in range(nmodels1):
    medvarToEA_1_gsat[i,:] = np.ma.median(varToEA_1_gsat[nruns:nruns+int(nMembers1_non0[i]),:],axis=0)
    medvarToEP_1_gsat[i,:] = np.ma.median(varToEP_1_gsat[nruns:nruns+int(nMembers1_non0[i]),:],axis=0)
    medvarToEI_1_gsat[i,:] = np.ma.median(varToEI_1_gsat[nruns:nruns+int(nMembers1_non0[i]),:],axis=0)
    nruns = nruns + int(nMembers1_non0[i])
    
if work != 'rcp85_histNat_1pctCO2_2std':
    nruns2=0
    medvarToEA_2_gsat = np.ma.masked_all((nmodels2,len(domains)))
    medvarToEP_2_gsat = np.ma.masked_all((nmodels2,len(domains)))
    medvarToEI_2_gsat = np.ma.masked_all((nmodels2,len(domains)))
    nMembers2_non0 = nMembers2[np.ma.nonzero(nMembers2)]
    for i in range(nmodels2):
        medvarToEA_2_gsat[i,:] = np.ma.median(varToEA_2_gsat[nruns2:nruns2+int(nMembers2_non0[i]),:],axis=0)
        medvarToEP_2_gsat[i,:] = np.ma.median(varToEP_2_gsat[nruns2:nruns2+int(nMembers2_non0[i]),:],axis=0)
        medvarToEI_2_gsat[i,:] = np.ma.median(varToEI_2_gsat[nruns2:nruns2+int(nMembers2_non0[i]),:],axis=0)
        nruns2 = nruns2 + int(nMembers2_non0[i])
    
# -- Organize data

# New domain labels
new_domains = ['SO subpolar', 'SH subtropics', 'NH subtropics', 'subpolar North Pacific']
# regroup previous "North Atlantic" with NH subtropics

data1 = [medvarToEA_1_gsat[:,1], medvarToEP_1_gsat[:,1], medvarToEI_1_gsat[:,1], maskdata, medvarToEA_1_gsat[:,0], medvarToEP_1_gsat[:,0], medvarToEI_1_gsat[:,0], maskdata, medvarToEA_1_gsat[:,3], medvarToEP_1_gsat[:,2], maskdata, medvarToEP_1_gsat[:,4]]

# tas ToE other case
if work == 'rcp85_histNat_1pctCO2_2std':
    data2 = [varToEA_2_gsat[:,1], varToEP_2_gsat[:,1], varToEI_2_gsat[:,1], maskdata, varToEA_2_gsat[:,0], varToEP_2_gsat[:,0], varToEI_2_gsat[:,0], maskdata, varToEA_2_gsat[:,3], varToEP_2_gsat[:,2], maskdata, varToEP_2_gsat[:,4]]
else:
    data2 = [medvarToEA_2_gsat[:,1], medvarToEP_2_gsat[:,1], medvarToEI_2_gsat[:,1], maskdata, medvarToEA_2_gsat[:,0], medvarToEP_2_gsat[:,0], medvarToEI_2_gsat[:,0], maskdata, medvarToEA_2_gsat[:,3], medvarToEP_2_gsat[:,2], maskdata, medvarToEP_2_gsat[:,4]]

# ----- Make pseudo-time axis with ranges -----

xgsat = np.arange(-1,6.01,0.02)
tickvalues = [1900,1980,2000,2020,2040,2060,2080,2100]
rangeticks = np.zeros((len(tickvalues),2)) # Initialize array with min and max of the members of a given year
for itick, timeval in enumerate(tickvalues):
    idx = np.argwhere(time1==timeval)[0][0]
    rangeticks[itick,0] = np.min(gsat_anom1_smooth[idx,:])
    rangeticks[itick,1] = np.max(gsat_anom1_smooth[idx,:])
newticknames2 = ['%d' % t for t in tickvalues]

# ----- Plot ------

y1 = 1850
y2 = 1900

labels = ['Atlantic','Pacific','Indian','','Atlantic','Pacific','Indian','','Atlantic','Pacific','','']
N = 13
ind = np.arange(1,N)
width = 0.25

fig, ax = plt.subplots(figsize=(11.5,13))

ax.axvline(x=1.5, color='black', ls=':')
ax.axvline(x=2, color='black', ls=':')
ax.axvline(x=0, color='black', ls=':')

red_crosses = dict(markeredgecolor='#c90016', marker='+',linewidth=0.5)
# ToE reference boxes
boxes1 = ax.boxplot(data1, vert=0, positions=ind-width, widths=width, whis=0,flierprops=red_crosses)
for box in boxes1['boxes']:
    box.set(color='#c90016', linewidth=2) #c90016 #ad3c48
for whisker in boxes1['whiskers']:
    whisker.set(color='#c90016', linestyle='-', linewidth=1)
for cap in boxes1['caps']:
    cap.set(color='#c90016', linewidth=1)
#for flier in boxes1['fliers']:
#    flier.set(color='#c90016')
for median in boxes1['medians']:
    median.set(color='#c90016', linewidth=2)


ax.set_xlim([-1,6.01])
ax.set_xlabel('GSAT anomaly ('+degree_sign+'C) relative to '+str(y1)+'-'+str(y2), fontweight='bold',fontsize=14)
ax.tick_params(axis='y',left=False, right=False, labelright=False, labelleft=True,pad=-10)#,pad=7)
ax.set_yticklabels(labels, horizontalalignment = 'left')
xmajorLocator = MultipleLocator(0.5)
xminorLocator = AutoMinorLocator(2)
ax.xaxis.set_major_locator(xmajorLocator)
ax.xaxis.set_minor_locator(xminorLocator)
ax.xaxis.set_tick_params(which='major',width=2)

ax2 = ax.twiny()
color_crosses = dict(markeredgecolor=color, marker='+',linewidth=0.5)
# ToE other case boxes
boxes2 = ax2.boxplot(data2, vert=0, positions=ind+width, widths=width, whis=0,flierprops=color_crosses)
for box in boxes2['boxes']:
    box.set(color=color, linewidth=2)
for whisker in boxes2['whiskers']:
    whisker.set(color=color, linestyle='-', linewidth=1)
for cap in boxes2['caps']:
    cap.set(color=color, linewidth=1)
for flier in boxes2['fliers']:
    flier.set(color=color)
for median in boxes2['medians']:
    median.set(color=color, linewidth=2)


ax2.set_xlim([-1,6.01])
ax2.set_yticks(ind)
ax2.set_yticklabels(['Atlantic','Pacific','Indian','','Atlantic','Pacific','Indian','','Atlantic','Pacific','',''])
ax2.tick_params(axis='y',labelleft=True,left=False,right=False,labelright=False,pad=-10)
ax2.set_ylim([0,N])
xmajorLocator2 = MultipleLocator(0.5)
xminorLocator2 = AutoMinorLocator(2)
ax2.xaxis.set_major_locator(xmajorLocator2)
ax2.xaxis.set_minor_locator(xminorLocator2)

plt.setp(ax2.get_yticklabels(), fontsize=12,fontweight='bold')
plt.setp(ax.get_yticklabels(), fontsize=12,fontweight='bold')
plt.setp(ax.get_xticklabels(), fontweight='bold',fontsize=14)
plt.setp(ax2.get_xticklabels(), fontweight='bold',fontsize=14)

ax2.axhline(y=ind[3], color='black', ls='--')
ax2.axhline(y=ind[7], color='black', ls='--')
ax2.axhline(y=ind[10], color='black', ls='--')

plt.subplots_adjust(left=0.15,right=0.87,top=0.91,bottom=0.11)

degree_sign= u'\N{DEGREE SIGN}'

# Domain labels
ax2.text(-1.8,ind[1], 'SO \n subpolar', ha='center', va='center', fontweight='bold', fontsize=13)
ax2.text(6.6,ind[1], '~40-60'+degree_sign+'S \n ~27-28kg.m-3', ha='center', va='center', fontsize=12)
ax2.text(-1.8,ind[5], 'SH \n subtropics', ha='center', va='center', fontweight='bold', fontsize=13)
ax2.text(6.6,ind[5], '~20-40'+degree_sign+'S \n ~25-26.5kg.m-3', ha='center', va='center', fontsize=12)
ax2.text(-1.8,ind[8]+0.5, 'NH \n subtropics', ha='center', va='center', fontweight='bold', fontsize=13)
ax2.text(6.6,ind[8], '~20-40'+degree_sign+'N \n ~26-27kg.m-3', ha='center', va='center', fontsize=12)
ax2.text(6.6,ind[9], '~20-40'+degree_sign+'N \n ~25-26kg.m-3', ha='center', va='center', fontsize=12)
ax2.text(-1.8,ind[11], 'Subpolar \n North Pacific', ha='center', va='center',fontweight='bold', fontsize=13)
ax2.text(6.6,ind[11], '~40-60'+degree_sign+'N \n ~26-27kg.m-3', ha='center', va='center', fontsize=12)

ax2.text(0.5,1.04, title1 + ' ('+str(nmodels1)+' models)', color='#c90016',
         va='center', ha='center',transform=ax2.transAxes, fontweight='bold')
ax2.text(0.5,1.062, title2 + ' ('+str(nmodels2)+' models)', color=color,
         va='center', ha='center',transform=ax2.transAxes, fontweight='bold')

# Date
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")

# -- Make pseudo-time x axis below the original one
#ax3 = ax.twiny()
ax3 = fig.add_axes([0.15,0.01,0.72,0.1])
ax3.set_xlim([-1,6.01])
ax3.set_ylim([-1.5,0])
ax3.set_frame_on(False)
ax3.axes.get_xaxis().set_visible(False)
ax3.axes.get_yaxis().set_visible(False)

for i in range(len(newticknames2)):
    if i%2 == 0:
        ax3.hlines(y=-1, xmin=rangeticks[i,0], xmax=rangeticks[i,1],linewidth=1.5,color='k')
        ax3.text((rangeticks[i,0] + rangeticks[i,1])/2, -0.95, newticknames2[i], fontweight='bold', va='bottom', ha='center')
    elif i==1 or i==5:
        ax3.hlines(y=-1.105, xmin=rangeticks[i,0], xmax=rangeticks[i,1],linewidth=1.5,color='k')
        ax3.text((rangeticks[i,0] + rangeticks[i,1])/2, -1.2, newticknames2[i], fontweight='bold', va='top', ha='center')
    else:
        ax3.hlines(y=-1.2, xmin=rangeticks[i,0], xmax=rangeticks[i,1],linewidth=1.5,color='k')
        ax3.text((rangeticks[i,0] + rangeticks[i,1])/2, -1.25, newticknames2[i], fontweight='bold', va='top', ha='center')


if outfmt == 'view':
    plt.show()
else:
    plt.savefig('suppboxplot_'+work+'.png',dpi=150)    
