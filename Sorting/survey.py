global csv, np, scipy, re, namedtuple
import csv
import numpy as np
import scipy
import re
from collections import namedtuple

def read (file_name, num_cols_survey_one, diag):      
    line_count = 0
    error_lines = []
    data_read = []
    with open(file_name, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for row in reader:
            line_count += 1
            if not row:  # Check if row is empty
                continue
            if len(row) != num_cols_survey_one:  # Check if row has the expected number of columns
                error_lines.append(line_count)
                continue
            data_read.append(row)
    if diag:
        print('SurveyData (pre-matching)')
        print('Error on lines:', error_lines)
        print('Number of errors:', len(error_lines))
        print('Size', len(data_read))
    return data_read, error_lines

def process_combine (data_read, survey_lst, num_cols, df, diag):
#
    #import numpy as np
    survey_lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 24, 26, 28, 30, 33, 36, 37, 39, 41, 44, 45, 55, 340, 341, 342, 343, 344, 345]
    rows_skipped = 0
    survey_names = [data_read[0][i] for i in survey_lst]

    num_rows_skipped = 0
    matched_rows = []
    total_matches = 0
    df_to_list = df["data_identifier"].to_list()
    for i, row in enumerate(data_read[1:]):  # skip the header row
        # skip row if it has fewer than the expected number of survey_lst
        #if len(row) < max(survey_lst) + 1:
        if len(row) < num_cols: # skip rows that contain less than 382 columns compared to 346 above
            num_rows_skipped += 1
            continue
        # skip row if case number doesn't match
        try:
            idx = df_to_list.index(row[16])
            values = [row[col] for col in survey_lst]
            values = [np.nan if v == ' ' else v for v in values]  # replace empty strings with NaN
            df.loc[idx, survey_names] = values
            total_matches += 1
            #continue
        except ValueError:
            #print('ValueError')
            #print('index', i)
            #print('value', row[16])
            continue
        # extract the values in the desired survey_lst
        #print('hello')    

    if diag:
    	print('SurveyData (post-matching)')
    	print('total matches', total_matches)
    	print('Number of rows skipped', num_rows_skipped)
    return df
    
def process (data_read, survey_lst, data_identifier, num_cols, diag):
    import numpy as np
    num_rows_skipped = 0
    matched_rows = []
    for i, row in enumerate(data_read[1:]):  # skip the header row
        # skip row if it has fewer than the expected number of survey_lst
        #if len(row) < max(survey_lst) + 1:
        if len(row) < num_cols: # skip rows that contain less than 382 columns compared to 346 above
            num_rows_skipped += 1
            continue
        # skip row if case number doesn't match
        if row[16] not in data_identifier:
            continue
        # extract the values in the desired survey_lst
        values = [row[col] for col in survey_lst]
        values = [np.nan if v == ' ' else v for v in values]  # replace empty strings with NaN
        try:
            float_values = [float(v) if float(v) <= 5 else np.nan for v in values]
            
        except ValueError:
            print('Row', i)
            print(f"Could not convert string to float: {values}")
            continue
        matched_rows.append(float_values)
    # convert matched rows to a numpy array
    data_arr = np.array(matched_rows)
    if diag:
        print('SurveyData (post-matching)')
        print('Number of rows skipped', num_rows_skipped)
        print('Size', np.shape(data_arr))
    return data_arr
    
    
def stats(data_arr, survey_lst, write, data_read):
    output = []
    survey_stats = namedtuple('survey', ['Survey_question_number', 'Survey_question', 'Number_of_responders', 'Number_of_non_responders', 'Mean', 'Median', 'Mode', 'Std', 'Skewness', 'Kurtosis', 'IQR', 'Maximum', 'Minimum'])

    mean_survey = np.nanmean(data_arr, axis=0)
    print('Shape of mean survey = ', str(np.shape(mean_survey)))
    std_survey = np.nanstd(data_arr, axis=0)
    median_survey = np.nanmedian(data_arr, axis=0)
    mode_survey = scipy.stats.mode(data_arr, axis=0, nan_policy='omit')    
    try:
        iqr_survey = np.subtract(*np.nanpercentile(data_arr, [75, 25], axis=0))
    except TypeError: # 07 / 2020
        iqr_survey = -1
    skew_survey = scipy.stats.skew(data_arr, axis=0, nan_policy='omit') 
    kurtosis_survey = scipy.stats.kurtosis(data_arr, axis=0, nan_policy='omit') 
    max_survey = np.nanmax(data_arr, axis=0)
    min_survey = np.nanmin(data_arr, axis=0)

    # count the number of float values and NaN values along axis 0
    try: #07 / 2020
        num_floats = np.sum(~np.isnan(data_arr), axis=0)
    except ValueError:
        num_floats = -1
    try:
        num_nans = np.sum(np.isnan(data_arr), axis=0)
    except ValueError:
        num_nans = -1

    print("Number of floats along axis 0:", num_floats)
    print("Number of NaNs along axis 0:", num_nans)

    print('Survey Questions')
    for j in range(len(survey_lst)):
        print('\n'+'Question',j+1)
        print(re.match(r'.*\d+\S{1}(.*)[[\?|\\]|\\\]*\.', data_read[0][survey_lst[j]]).group(1),'?')
        print(num_floats[j])
        print(num_nans[j])
        print('%.3f'%mean_survey[j])       
        print('%.3f'%median_survey[j])
        print('%.3f'%mode_survey[0][0][j])
        print('%.3f'%std_survey[j])
        print('%.3f'%skew_survey[j])
        print('%.3f'%kurtosis_survey[j])
        print('%.3f'%iqr_survey[j])        
        print(max_survey[j])
        print(min_survey[j])
        stats = survey_stats(j+1, re.match(r'.*\d+\S{1}(.*)[[\?|\\]|\\\]*\.', data_read[0][survey_lst[j]]).group(1)+'?', num_floats[j], num_nans[j], mean_survey[j], median_survey[j], mode_survey[0][0][j], std_survey[j], skew_survey[j], kurtosis_survey[j], iqr_survey[j], max_survey[j], min_survey[j])
        output.append(stats)
    try:
        print('Survey stats dims = ',str(np.shape(output)))
    except ValueError:
        print('ValueError when getting SurveyStats dims')
    return output
