import re
import numpy as np
import pandas as pd
import csv
import io
import scipy
from collections import Counter
from collections import namedtuple
import os
import survey
import demographics
from datatopowerpoint import open_pptx
from datatopowerpoint import write_pptx_survey_data
from datatopowerpoint import close_pptx
import itertools
import importlib
from tkinter import Tcl
global df

survey_lst = [18, 19, 20, 22, 24, 26, 28, 30, 33, 36, 37, 39, 41, 44, 45, 55, 340, 341, 342, 343, 344, 345]
survey_fol = "./SurveyData "
survey_stats_rows = ['Number of Responses', 'Number of responses + no answer', 'Mean', 'Standard deviation', 'Median', 'IQR', 'Skewness', 'Kurtosis', 'Maximum', 'Minimum']

demo_fol = "./ChargeDemo/"
demo_stats_rows = ['', '']

num_cols = 382

num_months = 6 # number of cols in data survey

write_to_file = 0

debug = 1
try:
    read_bool
except NameError:
    read_bool = 0
    answer = "Y"
    df_pared_data = pd.DataFrame()
    np_demo_data = []
    np_survey_data = []
    demo_stats = []
    survey_stats = []
if read_bool:
    print("Variables exist in workspace. Do you want to overwrite?")
    answer = NULL
    while answer != "Y" or answer != "N":
        try:
            answer = input("Y/N")
        except:
            continue
    if answer == "Y": 
        df_pared_data = pd.DataFrame()
        np_demo_data = []
        np_survey_data = []
        demo_stats = []
        survey_stats = []

        read_bool = []
    