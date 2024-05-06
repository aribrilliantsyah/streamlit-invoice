import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import locale

bulan_translation = {
    1: 'Januari',
    2: 'Februari',
    3: 'Maret',
    4: 'April',
    5: 'Mei',
    6: 'Juni',
    7: 'Juli',
    8: 'Agustus',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'Desember'
}

def translate_bulan(bulan):
    return bulan_translation[bulan]

def left_align(s, props='text-align: left;'):
    return props

def format_rupiah(value):
    return f"IDR {locale.format_string('%d', value, grouping=True)}"


st.set_page_config(page_title='Database Invoice SIP')
st.header('Database Invoice SIP')
st.markdown('_Pengolahan Database Invoice SIP_')

### --- LOAD DATAFRAME
excel_file = 'INVOICE_2024.xlsx'
sheet_name = 'DATA'

df = pd.read_excel(excel_file,
                   sheet_name=sheet_name,
                   usecols='A:F',
                   header=0)


df = df.replace(np.nan, '', regex=True)
df = df.groupby(by=['periode', 'bpr', 'tahun', 'bulan', 'status', 'harga']).sum().reset_index()
df['bulan_number'] = df['bulan']
df['bulan'] = df['bulan'].apply(translate_bulan)
df['tahun'] = df['tahun'].astype(str)

st.dataframe(df)

# ## --- STREAMLIT SELECTION
periode = df['periode'].unique().tolist()
bpr_name = df['bpr'].unique().tolist()
tahun = df['tahun'].unique().tolist()
bulan = df['bulan'].unique().tolist()
status = df['status'].unique().tolist()
harga = df['harga'].unique().tolist()

# harga_selection = st.slider('Harga: ', 
#                           min_value = min(harga),
#                           max_value = max(harga),
#                           value=(min(harga), max(harga)))

bulan_selection = st.multiselect('Bulan: ',
                                bulan,
                                default=bulan)
                            
status_selection = st.multiselect('Status: ',
                                status,
                                default=status)

# --- FILTER DATAFRAME BASED ON SELECTION
mask = (df['status'].isin(status_selection) & 
        df['bulan'].isin(bulan_selection))

number_of_result = df[mask].shape[0]
st.markdown(f'*Hasil yang didapatkan: {number_of_result}*')

# --- GRAFIK AFTER SELECTION
# multiple line by status
df = df[mask]
df['group_date'] = df['bulan'] + ' ' + df['tahun'].astype(str)
df_sorted = df.sort_values(by=['bulan_number', 'tahun'], ascending=True)
df_summary = df_sorted.groupby(['bulan_number', 'tahun', 'group_date', 'status'])['harga'].sum().reset_index()

st.dataframe(df_summary)
chart = px.line(df_summary, x='group_date', y='harga', color='status', text='harga', title='Total Pendapatan dalam Bulan - Tahun',
            labels={'harga': 'Total Harga', 'group_date': 'Bulan-Tahun'},
            color_discrete_map={'PAID': 'green', 'UNPAID': 'red', 'WAITING_PAYMENT': 'blue'}
        )
chart.update_yaxes(tickformat=",.0f", title="Total Harga")

# Tampilkan grafik menggunakan Streamlit
st.plotly_chart(chart)

