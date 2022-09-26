#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pulse_survey.py
#  
#  Author katerinabc/ Katerina
 

# # # # # import libraries # # # # #
import json
import sys
import pandas as pd
import numpy as np
from sklearn import preprocessing

def soc(df, minscale, maxscale):
    """
    input the data export from blocksurvey

    Output:
    indi_SoC: average SoC per user
    SoC: Community's sense of community

    """
    d = dict()

    d['timestamp'] = min(df['Submitted At'])

    # # # Sense of Community # # #

    indi_SoC = (df['Soc_ec1_exp'] + df['Soc_ec2_exp'])/2

    scaler = preprocessing.MinMaxScaler(feature_range=(0, 100)) #normalize scores between 0 and 100
    # make sure the default range is from 1 to 5 like the scale
    df_default = np.array([minscale, maxscale])
    df_def = scaler.fit_transform(df_default.reshape(-1,1)) 
    
    indi_SoC_n = scaler.transform(indi_SoC.values.reshape(-1,1)) # reshape array from 2d to 1d, and normalize
    
    d['min_SoC']  = np.nanmin(indi_SoC_n).round(1)
    d['max_SoC']  = np.nanmax(indi_SoC_n).round(1)
    d['avg_SoC'] = np.nanmean(indi_SoC_n).round(1)
    d['sd_SoC'] = np.nanstd(indi_SoC_n).round(1)

    return d

#df = pd.DataFrame(data = soc(pd.read_csv('rndao_pulse2.csv')))

data = soc(pd.read_csv(sys.argv[1]), sys.argv[2], sys.argv[3])

#json file needs to include: timestamp, soc

json_object = json.dumps(data, indent = 4) 
with open('pulse.json', 'w') as outfile:
    json.dump(json_object, outfile)