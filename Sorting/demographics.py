global pd, re, np, namedtuple, Counter, scipy, dataclass, csv
import pandas as pd
import re
import numpy as np
import csv
from collections import namedtuple
from collections import Counter
import scipy
from dataclasses import dataclass


def make_ratio_var_stats(numpy_patient_data, data_cat, isint):
    my_stats = namedtuple('my_stats', ['Count', 'NanNumber', 'Mean', 'Median', 'Mode', 'Std', 'Skewness', 'Kurtosis', 'IQR', 'Maximum', 'Minimum'])    
    # Case Length Stats    
    #count = Counter((numpy_patient_data[:, data_cat]).tolist())
    try:
        if isint == 0:  
            data_float = (numpy_patient_data[:, data_cat]).astype(float)
            count = Counter(data_float)
            numnans = sum(np.isnan(data_float))
            mean = np.nanmean(data_float)
            median = np.nanmedian(data_float)
            mode = scipy.stats.skew(data_float, nan_policy='omit')
            std = np.nanstd(data_float.astype(float))
            #var = np.nanvar((numpy_patient_data[:, data_cat]).astype(float))
            skew = scipy.stats.skew(data_float, nan_policy='omit')
            kurtosis = scipy.stats.kurtosis(data_float, nan_policy='omit') 
            iqr = np.subtract(*np.nanpercentile(data_float, [75, 25]))
            maximum = np.nanmax(data_float, axis=0)
            minimum = np.nanmin(data_float, axis=0)
        else:
            # Convert data to float64 first
            data_float = numpy_patient_data[:, data_cat].astype(np.float64)
            nan_mask = (data_float == -9223372036854775808)
            data_float[nan_mask] = np.nan
            #data_int = np.nan_to_num(data_float).astype(np.int64)
            data_int = data_float
            numnans = sum(np.isnan(data_int))
            count = Counter(data_int)
            data_of_interest = [tup[1] for tup in count.most_common()]
            mean = np.nanmean(data_of_interest)
            median = np.nanmedian(data_of_interest)
            mode = scipy.stats.skew(data_of_interest, nan_policy='omit')
            std = np.nanstd(data_of_interest)
            #var = np.nanvar((numpy_patient_data[:, data_cat]).astype(float))
            skew = scipy.stats.skew(data_of_interest, nan_policy='omit')
            kurtosis = scipy.stats.kurtosis(data_of_interest, nan_policy='omit') 
            iqr = np.subtract(*np.nanpercentile(data_of_interest, [75, 25]))
            maximum = np.nanmax(data_of_interest, axis=0)
            minimum = np.nanmin(data_of_interest, axis=0)
            output = my_stats(count, numnans, mean, median, mode, std, skew, kurtosis, iqr, maximum, minimum) 
        return output
    except:
        print('Probably error with numpy_patient_data[:, data_cat]')
        return None
    

def print_ratio_var_stats(statistics, cast_to_int): 
    try:
        mostcommon = statistics.Count.most_common(10)
        print('Most Common')
        if cast_to_int:
            for x in range(len(mostcommon)):
                print(np.int64(mostcommon[x][0]), mostcommon[x][1]) 
        else:
            for x in range(len(mostcommon)):
                print(mostcommon[x][0], mostcommon[x][1])     
        print('Number of NaNs =', '%.3f'%statistics.NanNumber)
        print('Mean =', '%.3f'%statistics.Mean)
        print('Median =', '%.3f'%statistics.Median)
        print('Mode =', '%.3f'%statistics.Mode)
        print('Standard Deviation =', '%.3f'%statistics.Std)
        #print('Variance =', var_case_length)
        print('Skew =', '%.3f'%statistics.Skewness)
        print('Kurtosis =', '%.3f'%statistics.Kurtosis)
        print('IQR =', '%.3f'%statistics.IQR)
        print('Max =', '%.3f'%statistics.Maximum)
        print('Min =', '%.3f'%statistics.Minimum)
    except:
        print('Error printing ratio var stats')

def make_nominal_var_stats(numpy_patient_data, data_cat):
    try:
        #my_stats = namedtuple('my_stats', ['Count', 'NanNumber', 'Mode'])
        my_stats = namedtuple('my_stats', ['Count', 'Mode'])
        count = Counter((numpy_patient_data[:, data_cat]).tolist())
        #numnans = np.isnan((numpy_patient_data[:, data_cat]).tolist())
        mode = scipy.stats.mode((numpy_patient_data[:, data_cat]).tolist(), nan_policy='omit')    
        output = my_stats(count, mode)
        return output
    except:
        print('Nominal var stats error')
        return None

def print_nominal_var_stats(statistics):
    try:
        mostcommon = statistics.Count.most_common(10)   
        print('Most Common')
        for x in range(len(mostcommon)):        
            print(mostcommon[x][0], mostcommon[x][1])   
    except:
        print('Error printing nominal var stats')

#def store_stats():
    #if true#change this
    #    store_ratio_var_stats()
    #if true#change this
    #    store_nominal_var_stars()
    
#def store_ratio_var_stats(stats_group):

#def store_nominal_var_stars(stats_group):

def read (file_name):
    #import numpy as np
 
    df = pd.read_fwf(file_name, skiprows=[1])
    print('Df type == ',str(type(df)))
    data_identifier = []
    visit_sid = []
    python_data_index = []
    p = re.compile(r'\d+')
    for x in range(np.shape(df)[0]):
        try:
            output = re.findall(p, df.loc[x][9])     #Unique Identifier, string
        except TypeError: #last element seems to have NaN which otw crashes code
            break
        data_identifier.append(output[0])
        visit_sid.append(df.loc[x][0]) # integer 64
        python_data_index.append(x)
    return df, data_identifier, visit_sid, python_data_index
    
def process(data_identifier, survey_data, error_lines, df: pd.core.frame.DataFrame, diag):
    #Patient = namedtuple("Patient", ["VisitSID", "MatchKeytoCaseNumber", "TotalChargeMinutes", "FacilityName", "PhysicalStatus", "PlaceOfServiceCode", "SurgeonNPI", "ASADesc", "CPT", "CPTClinicalCategory", "Emergent", "PatientAge", "PatientGender", "PrimaryDoctorNPI", "PrimaryNurseNPI", "USAPRegion"])
    patient_data = []
    test_cols = list(df.columns)
    test_cols.append('data_identifier')
    df_temp = pd.DataFrame(columns = test_cols)
    data_counter = 0
    print('Df type == ',str(type(df)))
    for x in range(len(survey_data)):
        try: #check if line contains error, the go to next iteration
            if error_lines.index(x) >= 0:
                #print('Is it fixed')
                continue
        except: #Here is the code we WANT to run if error line not found above 
            try:
                python_data_var = data_identifier.index(survey_data[x][16])
                #python_data_var = (data_identifier == data_read[x][16])
                python_data_var2 = python_data_var + 1
                df_new = pd.DataFrame(data=df.iloc[python_data_var:python_data_var2,:].values, columns = df.columns)
                df_new['data_identifier'] = survey_data[x][16]
                #type(df_temp)
                df_temp = pd.concat([df_temp, df_new], ignore_index=True)
                data_counter += 1
                if data_counter % 1000 == 0:
                    print('1000 checkpoint')
            except ValueError: #key not found, continue
                continue      
    print('df_temp shape',str(df_temp.shape))     
    #numpy_patient_data = np.array(patient_data)
    return df_temp #numpy_patient_data, df_temp
    
def stats(numpy_patient_data, write):
    provider = 1
    demo_stats = namedtuple('demo_stats', ['case_length', 'facility_name', 'physical_status', 'place_of_service', 'surg_npi', 'asa_desc', 'cpt', 'cpt_cat', 'emergent', 'age', 'gender', 'anes_npi', 'nurse_npi', 'usap_region'])
    # Case Length
    case_length_cols = 2
    case_length_stats = make_ratio_var_stats(numpy_patient_data, case_length_cols, 0)
    print('\nCase Length')
    print_nominal_var_stats(case_length_stats)        
    # Facility Name Stats
    facility_name_cols = 3
    facility_name_stats = make_nominal_var_stats(numpy_patient_data, facility_name_cols)
    print('\nFacilities')
    print_nominal_var_stats(facility_name_stats)   
    # Physical Status
    physical_status_cols = 4
    phys_status_stats = make_nominal_var_stats(numpy_patient_data, physical_status_cols)
    print('\nPhysical Status')
    print_nominal_var_stats(phys_status_stats)            
    # Place of Service Code
    place_service_cols = 5
    place_of_service_stats = make_nominal_var_stats(numpy_patient_data, place_service_cols)
    print('\nPlace of Service')
    print_nominal_var_stats(place_of_service_stats)    
    # SurgeonNPI
    surgeon_npi_cols = 6
    surgeon_npi_stats = make_ratio_var_stats(numpy_patient_data, surgeon_npi_cols, 1)    
    print('\nSurgeon')
    print_ratio_var_stats(surgeon_npi_stats, provider)    
    # ASADesc
    asa_cols = 7
    asa_desc_stats = make_nominal_var_stats(numpy_patient_data, asa_cols)
    print('\nASA Desc')
    print_nominal_var_stats(asa_desc_stats)    
    # CPT code
    cpt_cols = 8
    cpt_stats = make_nominal_var_stats(numpy_patient_data, cpt_cols)
    print('\nCPT')
    print_nominal_var_stats(cpt_stats)    
    # CPT categories
    cpt_cat_cols = 9
    cpt_cat_stats = make_nominal_var_stats(numpy_patient_data, cpt_cat_cols)
    print('\nCPT Categories')
    print_nominal_var_stats(cpt_cat_stats)    
    # Emergent
    emergent_cols = 10
    emergent_stats = make_nominal_var_stats(numpy_patient_data, emergent_cols)
    print('\nEmergent')
    print_nominal_var_stats(emergent_stats)
    # Patient Age
    patient_age_cols = 11
    age_stats = make_ratio_var_stats(numpy_patient_data, patient_age_cols, 1)    
    print('\nPatient Age')
    print_ratio_var_stats(age_stats, 0)
    # Patient Gender
    gender_cols = 12
    gender_stats = make_nominal_var_stats(numpy_patient_data, gender_cols)
    print('\nGender')
    print_nominal_var_stats(gender_stats)
    # AnesthesiologistNPI
    anesnpi_cols = 13
    anes_npi_stats = make_ratio_var_stats(numpy_patient_data, anesnpi_cols, 1)    
    print('\nAnesthesiologist')
    print_ratio_var_stats(anes_npi_stats, provider)     
    # NurseNPI
    nurse_npi_cols = 14
    nurse_npi_stats = make_ratio_var_stats(numpy_patient_data, nurse_npi_cols, 1)    
    print('\nNurse')
    print_ratio_var_stats(nurse_npi_stats, provider) 
    # USAP Region
    usapreg_cols = 15
    usapreg_stats = make_nominal_var_stats(numpy_patient_data, usapreg_cols)
    print('\nUSAP Region')
    print_nominal_var_stats(usapreg_stats)   
    output = demo_stats(case_length_stats, facility_name_stats, phys_status_stats, place_of_service_stats, surgeon_npi_stats, asa_desc_stats, cpt_stats, cpt_cat_stats, emergent_stats, age_stats, gender_stats, anes_npi_stats, nurse_npi_stats, usapreg_stats)
    try:
        print('Demo stats dims = ',str(np.shape(output)))
    except ValueError:
        print('Demo stats dims = ,str(np.shape(output)) - ValueError:setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (14,) + inhomogeneous part.')
    return output