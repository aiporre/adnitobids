import pandas as pd

data_1 = "/media/sauron/Extreme SSD/ADNI/adni_zips/gld_benchmark_MRI_Images_27Feb2025.csv"
data_2 = "/media/sauron/Extreme SSD/ADNI/adni_zips/gld_benchmark_My_Table_27Feb2025.csv"

df_1 = pd.read_csv(data_1)
df_2 = pd.read_csv(data_2)
print('-------------------------')
# print(df_1.head())
print(df_1.columns)
print('-------------------------')
print('-------------------------')
print('-------------------------')
print('-------------------------')
# print(df_2.head())
print(df_2.columns)

# generate fields of MPRAGEMETA.csv
# df 1 has " Index(['image_id', 'subject_id', 'study_id', 'mri_visit', 'mri_date',
#        'mri_description', 'image_type', 'mri_type', 'mri_weighting',
#        'mri_sequence', 'mri_thickness', 'mri_te', 'mri_tr', 'mri_ti',
#        'mri_coil', 'mri_flip_angle', 'mri_acq_plane', 'mri_width',
#        'mri_height', 'mri_n_images', 'mri_pixel_x', 'mri_pixel_y', 'mri_mfr',
#        'mri_mfr_model', 'mri_field_str', 'mri_processing'],
#       dtype='object')
# ----------------------
# df 2 has columns
# Index(['subject_id', 'visit', 'subject_age', 'research_group', 'BCPREDX'], dtype='object')
# ----------------------
df_out = pd.DataFrame()
df_out['Orig/Proc'] = df_1["image_type"]
df_out['SubjectID'] = df_1["subject_id"]
df_out['Visit'] = df_1['mri_visit']
df_out['MagStrength'] = 1.5
df_out['Sequence'] = df_1["mri_description"]
df_out['ScanDate'] = df_1["mri_date"]
df_out['StudyID'] = df_1['study_id']
df_out['SeriesID'] = df_1['image_id']
df_out['ImageUID'] = df_1['image_id']
print(df_out.iloc[0])
print(df_out['Orig/Proc'].unique())
df_out.to_csv('MPRAGEMETA_27Feb2025.csv', index=False)



