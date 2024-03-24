from usapstatsheader import * # overwrites data

demo_file = os.listdir(demo_fol)

#total_elements = os.listdir(survey_fol_work)
try:
    answer
except NameError:
    answer = "Y"
if answer == "Y": # data overwritten in usapstatsheader 
    read_bool = 1
    for i in range(len(demo_file)):
        demo_path = demo_fol + demo_file[i]
        df, data_identifier, visit_sid, python_data_index = demographics.read(demo_path)
        print('Df type == ',str(type(df)))
        print('df.loc[]')
        # Only one years' worth of is presented to inner loop and stats functions
        survey_fol_work = survey_fol + str(i + 2019) + "/"
        survey_file = os.listdir(survey_fol_work)
        subset_size = len(survey_file)
        for j in range(len(survey_file)):
            survey_index = j * (i+1) # change to i+1 for full dataset starting at 2019
            demo_index = j * (i+1)
            survey_path = survey_fol_work + survey_file[j]
            survey_data, error_lines = survey.read(survey_path, num_cols, debug)
            np_demo_data.append(demographics.process(data_identifier, survey_data, error_lines, df, debug))        
            np_survey_data.append(survey.process(survey_data, survey_lst, data_identifier, num_cols, debug))        
            print('Demographic Statistics for', (re.findall(r'(\d{4})\_(\d{2})\_\w+\.\w{3}', survey_file[j]))[0][1], (re.findall(r'(\d{4})\_(\d{2})\_\w+\.\w{3}', survey_file[j]))[0][0])
            demo_stats.append(demographics.stats(np_demo_data[demo_index], write_to_file))
            print('Survey Statistics for', (re.findall(r'(\d{4})\_(\d{2})\_\w+\.\w{3}', survey_file[j]))[0][1], (re.findall(r'(\d{4})\_(\d{2})\_\w+\.\w{3}', survey_file[j]))[0][0])
            survey_stats.append(survey.stats(np_survey_data[survey_index], survey_lst, write_to_file, survey_data))    
        print('Checkpoint main')
        prs, slide_layout = open_pptx(2019, i)
        # Write survey data
        a = np.int32(len(survey_file)/num_months)
        slide_index = 0
        for c in range(0, a): 
            start_index = (len(survey_file) * i) + (num_months * c) # requires the i survey_file folders to contain the same number of elements
            end_index = (len(survey_file) * i) + (num_months * c) + num_months
            print('Checkpoint main')
            prs, slide_index = write_pptx_survey_data(prs, slide_layout, slide_index, num_months, survey_stats[start_index:end_index], survey_file)
        # Write demographic data    
        #for c in range(0, len(survey_file)):
        #    prs, slide_index = write_pptx_demo_ratio_data(prs, slide_layout, slide_index, demo_stats[c], survey_file[c])
        #    prs, slide_index = write_pptx_demo_nominal_data(prs, slide_layout, slide_index, demo_stats[c], survey_file[c])
        close_pptx(2019, i, prs)
else: 
    print("No data modified")
