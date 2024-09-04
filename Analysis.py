# Challenge 120: Data Analysis
# _
# This script loads results of Jonas Deichmann's Challenge 120 [1] from
# triathlon-szene.de [2] and visualizes time splits (Swim, Bike, Run,
# T1, Lunch, T2, Total) as day-to-day plots with moving averages.
# 
# Daily results should be stored as a file called "Results.txt" and the
# script will then save results into files "Figure_1|2|3|4.png".
# 
# [1] https://jonasdeichmann.com/challenge-120/
# [2] https://www.triathlon-szene.de/forum/showpost.php?p=1747596&postcount=1
# 
# Author: Joram Soch
# E-Mail: JoramSoch@web.de
# 
# Version History:
# - 26/07/2024, 23:11: initial version
# - 30/07/2024, 13:34: splitted bike times
# - 25/08/2024, 22:43: added y-axis labels
# - 04/09/2024, 13:43: minor changes, some documentation


# import modules
import math
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# load data
filename = 'Results.txt'
file_obj = open(filename, 'r')
file_txt = file_obj.readlines()
file_obj.close()

# specify settings
N   = 120                       # total number of triathlons
w   = 7                         # sliding window widths
d0  = 4                         # label starting date
dd  = 7                         # label date interval
dCR = 60                        # Challenge Roth day

# preallocate results
L = ['Swim', 'T1', 'Bike', 'Lunch', 'T2', 'Run', 'Total', 'Bike1', 'Bike2']
T = np.zeros((N,len(L)))
D = [''] * N
i = -1

# for each line in file
for line in file_txt:
    
    # if this is a long-distance triathlon
    if '. LD' in line or '.LD' in line:
        i = i + 1
        
        # extract Date
        di   = dt.date(2024,5,9) + dt.timedelta(days=i)
        D[i] = '{:02d}.{:02d}.'.format(di.day, di.month)
        # j1   = line.find('(')+1
        # j2   = line.find(')')
        # D[i] = line[j1:j2]
        
        # extract Swim
        j1 = line.find('.)')+3
        j2 = line.find('h',j1)
        try:
            T[i,0] = int(line[j1]) + int(line[j1+2:j2])/60
        except ValueError:
            T[i,0] = np.nan
        
        # extract T1
        j1 = line.find('|',j2)+2
        j2 = line.find('m',j1)
        try:
            T[i,1] = int(line[j1:j2])/60
        except ValueError:
            T[i,1] = np.nan
        
        # extract Bike
        j1 = line.find('|',j2)+2
        j2 = line.find('h',j1)
        try:
            T[i,2] = int(line[j1]) + int(line[j1+2:j2])/60
        except ValueError:
            T[i,2] = np.nan
        T[i,7] = T[i,2]/2
        T[i,8] = T[i,2]/2
        
        # extract Lunch
        j1 = line.find('|',j2)+2
        j2 = line.find('m',j1)
        try:
            T[i,3] = int(line[j1:j2])/60
        except ValueError:
            T[i,3] = np.nan
        
        # extract T2
        j1 = line.find('|',j2)+2
        j2 = line.find('m',j1)
        try:
            T[i,4] = int(line[j1:j2])/60
        except ValueError:
            T[i,4] = np.nan
        
        # extract Run
        j1 = line.find('|',j2)+2
        j2 = line.find('h',j1)
        try:
            T[i,5] = int(line[j1]) + int(line[j1+2:j2])/60
        except ValueError:
            T[i,5] = np.nan
        
        # extract Total
        j1 = line.find('||',j2)+3
        j2 = line.find('h',j1)
        try:
            T[i,6] = int(line[j1:j1+2]) + int(line[j1+3:j2])/60
        except ValueError:
            T[i,6] = np.nan

# prepare date label indices
n  = i + 1
x  = np.arange(1, n+1, dtype=np.int32)
di = np.arange(d0, N, dd, dtype=np.int32)
ds = [D[i-1] for i in di]

# smooth daily times
S = np.zeros(T.shape)
for j in range(T.shape[1]):
    t = T[0:n,j]
    for i in x:
        S[i-1,j] = np.nanmean(t[np.logical_and(x>i-w/2, x<i+w/2)])

# find first missing data
dMD = np.min(np.where(np.isnan(T[:,6])))+1

# function: decimal to hours
def dec2hm(h):
    hm = '{:02d}:{:02d}'.format(math.floor(h), round((h-math.floor(h))*60))
    return hm

# function: decimal to minutes
def dec2ms(m):
    ms = '{:02d}:{:02d}'.format(math.floor(m), round((m-math.floor(m))*60))
    return ms

# Figure 1: stacked bar plot
discs =['Swim', 'T1', 'Bike1', 'Lunch', 'Bike2', 'T2', 'Run']
cols  = 'bygmgcr'
fig   = plt.figure(figsize=(16,9))
ax    = fig.add_subplot(111)
curr  = np.zeros(n)
for k, disc in enumerate(discs):
    j = L.index(disc)
    ax.bar(x, T[0:n,j], 0.8, bottom=curr, color=cols[k], label=disc)
    curr = curr + T[0:n,j]
ax.set_xticks(di, labels=ds)
yt = ax.get_yticks()
ax.set_yticks(yt, [dec2hm(h) for h in yt])
ax.axis([(1-1), (N+25), 0, 16])
ax.legend(loc='upper right', fontsize=20)
ax.tick_params(axis='x', labelsize=13)
ax.tick_params(axis='y', labelsize=17)
ax.set_xlabel('day [date]', fontsize=20)
ax.set_ylabel('time [h]', fontsize=20)
ax.set_title('Challenge 120: All Days, All Times', fontsize=32)
ax.text(x[dCR-1], 16-0.2, 'Challenge Roth\n|\nV', fontsize=14,
        horizontalalignment='center', verticalalignment='top')
ax.text(x[dMD-1], 16-0.2, 'missing data\n|\nV', fontsize=14,
        horizontalalignment='center', verticalalignment='top')
ax.text(N+2.5, 8, 'Note: Bike1 and\nBike2 are not\nmeasured, but\ninterpolated (half\nof total bike time).',
        horizontalalignment='left', verticalalignment='top', fontsize=14)

fig.savefig('Figure_1.png', dpi=300, transparent=True)

# Figure 2: smoothed disciplines
discs =['Swim','Bike','Run']
cols  = 'bgr'
lims  = np.array([[1+ 4/60, 1+22/60], [5+45/60, 7+ 5/60], [4+ 0/60, 5+10/60]])
fig   = plt.figure(figsize=(16,16))
axs   = fig.subplots(3,1)
for k, disc in enumerate(discs):
    j = L.index(disc)
    axs[k].plot(x, T[0:n,j], 'o'+cols[k], label=disc+': daily times')
    axs[k].plot(x, S[0:n,j], '-'+cols[k], label=str(w)+'-day rolling average')
    axs[k].set_xticks(di, labels=ds)
    yt = axs[k].get_yticks()
    axs[k].set_yticks(yt, [dec2hm(h) for h in yt])
    axs[k].axis([(1-1), (N+1), lims[k,0], lims[k,1]])
    axs[k].legend(loc='lower right', fontsize=16)
    if disc == 'Swim': axs[k].legend(loc='lower center', fontsize=16)
    axs[k].tick_params(axis='x', labelsize=14)
    axs[k].tick_params(axis='y', labelsize=16)
    if k == 0:
        axs[k].set_title('Challenge 120: '+', '.join(discs), fontsize=32)
    if k == 2:
        axs[k].set_xlabel('day [date]', fontsize=20)
    axs[k].set_ylabel('time [h]', fontsize=20)
    axs[k].text(x[dCR-1], T[dCR-1,j], ' Challenge Roth', fontsize=16,
                horizontalalignment='left', verticalalignment='bottom')
fig.savefig('Figure_2.png', dpi=300, transparent=True)

# Figure 3: smoothed breaks
discs =['T1','Lunch','T2']
cols  = 'ymc'
lims  = np.array([[14, 46], [-1, 71], [6, 44]])
fig   = plt.figure(figsize=(16,16))
axs   = fig.subplots(3,1)
for k, disc in enumerate(discs):
    j = L.index(disc)
    axs[k].plot(x, T[0:n,j]*60, 'o'+cols[k], label=disc+': daily times')
    axs[k].plot(x, S[0:n,j]*60, '-'+cols[k], label=str(w)+'-day rolling average')
    axs[k].set_xticks(di, labels=ds)
    yt = axs[k].get_yticks()
    axs[k].set_yticks(yt, [dec2ms(m) for m in yt])
    axs[k].axis([(1-1), (N+1), lims[k,0], lims[k,1]])
    axs[k].legend(loc='lower right', fontsize=16)
    axs[k].tick_params(axis='x', labelsize=14)
    axs[k].tick_params(axis='y', labelsize=16)
    if k == 0:
        axs[k].set_title('Challenge 120: '+', '.join(discs), fontsize=32)
    if k == 2:
        axs[k].set_xlabel('day [date]', fontsize=20)
    axs[k].set_ylabel('time [min]', fontsize=20)
    axs[k].text(x[dCR-1], T[dCR-1,j]*60, ' Challenge Roth', fontsize=16,
                horizontalalignment='left', verticalalignment='bottom')
fig.savefig('Figure_3.png', dpi=300, transparent=True)

# Figure 4: smoothed total time
disc = 'Total'
col  = 'goldenrod'
lims = np.array([11+30/60, 15+30/60])
fig  = plt.figure(figsize=(16,9))
ax   = fig.add_subplot(111)
j    = L.index(disc)
ax.plot(x, T[0:n,j], 'o', color=col, label=disc+': daily times')
ax.plot(x, S[0:n,j], '-', color=col, label=str(w)+'-day rolling average')
ax.set_xticks(di, labels=ds)
yt = ax.get_yticks()
ax.set_yticks(yt, [dec2hm(h) for h in yt])
ax.axis([(1-1), (N+1), lims[0], lims[1]])
ax.legend(loc='lower left', fontsize=20)
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=17)
ax.set_xlabel('day [date]', fontsize=20)
ax.set_ylabel('time [h]', fontsize=20)
ax.set_title('Challenge 120: All Days, Total Time', fontsize=32)
ax.text(x[dCR-1], T[dCR-1,j], ' Challenge Roth', fontsize=20,
        horizontalalignment='left', verticalalignment='bottom')
fig.savefig('Figure_4.png', dpi=300, transparent=True)