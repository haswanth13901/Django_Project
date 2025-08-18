import os
import django
import pandas as pd
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from fhirapi.models import Doctor

columns = [
    'npi', 'ind_pac_id', 'ind_enrl_id', 'provider_last_name', 'provider_first_name',
    'provider_middle_name', 'suff', 'gndr', 'cred', 'med_sch', 'grd_yr',
    'pri_spec', 'sec_spec_1', 'sec_spec_2', 'sec_spec_3', 'sec_spec_4',
    'sec_spec_all', 'telehlth', 'facility_name', 'org_pac_id', 'num_org_mem',
    'adr_ln_1', 'adr_ln_2', 'ln_2_sprs', 'city_town', 'state', 'zip_code',
    'telephone_number', 'ind_assgn', 'grp_assgn', 'adrs_id'
]

file_path = "C:\\Users\\lenovo\\OneDrive\\Desktop\\Django Doctor Finder\\healthcare-app\\backend\\RawData_DAC_NationalDownloadableFile.csv"
output_path = "C:\\Users\\lenovo\\OneDrive\\Desktop\\Django Doctor Finder\\healthcare-app\\backend\\filtered_doctors.csv"

df = pd.read_csv(file_path, names=columns, header=None, low_memory=False)

if df.iloc[0]['provider_first_name'].strip().lower() == 'provider first name':
    df = df.iloc[1:]

required_cols = ['ind_pac_id', 'provider_first_name', 'provider_last_name', 'pri_spec', 'telephone_number',
                 'adr_ln_1', 'city_town', 'state', 'zip_code']
df = df.dropna(subset=required_cols)

df = df.drop_duplicates(subset='ind_pac_id')

df['address'] = (
    df['adr_ln_1'].fillna('') + ', ' +
    df['adr_ln_2'].fillna('')
)

def generate_email(first, last):
    domain = random.choice(['gmail.com', 'yahoo.com', 'docmail.com', 'healthpro.org'])
    user = (first[:1] + last + ''.join(random.choices(string.digits, k=3))).lower()
    return f"{user}@{domain}"

df['email'] = df.apply(lambda row: generate_email(row['provider_first_name'], row['provider_last_name']), axis=1)

df_filtered = df[[ 
    'ind_pac_id', 'provider_first_name', 'provider_last_name', 'pri_spec', 'telephone_number', 
    'email', 'address', 'city_town', 'state', 'zip_code'
]].rename(columns={
    'ind_pac_id': 'practitioner_id',
    'provider_first_name': 'first_name',
    'provider_last_name': 'last_name',
    'pri_spec': 'specialization',
    'telephone_number': 'phone',
    'city_town': 'city'
})

df_filtered.to_csv(output_path, index=False)
print(f"Cleaned data is saved at: {output_path}")
