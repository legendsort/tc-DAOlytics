#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compute_interaction_network_test.py
#
#  Author Ene SS Rawa / Tjitse van der Molen


# # # # # import libraries # # # # #
import sys
import numpy as np
from datetime import datetime

import network_functions as nf



# # # # # main function # # # # #

def main(args):
    """
    Run compute network function with test data
    """

    # set parameters for analysis
    db_path = "mongodb://tcmongo:T0g3th3rCr3wM0ng0P55@104.248.137.224:1547/?authMechanism=DEFAULT"
    guild = '993163081939165234'
    acc_names = ["sepehr#3795", "mehrdad_mms#8600", "Behzad#1761", "thegadget.eth#3374"] # should be all active accounts
    last_date = datetime(2023, 1, 16) # should be the last date of the analysis range (most recent date)
    day_range = 365 # should be set in initial settings or default of 7. A high value was used here due to sparse data in dev db
    channel_selection = ["993163081939165240"] # should be all channels or a subset selected by user

    # run script
    network_analysis_out = nf.discord_interact_analysis_main(guild, db_path, acc_names, last_date, day_range, channel_selection)

    print(network_analysis_out)


if __name__ == '__main__':
    sys.exit(main(sys.argv))