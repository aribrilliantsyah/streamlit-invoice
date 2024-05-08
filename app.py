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


st.set_page_config(page_title='Data Invoice SIP')
st.header('Data Invoice SIP')
st.markdown('_Pengolahan Data Invoice SIP_')

### --- LOAD DATAFRAME
excel_file = 'INVOICE_2024.xlsx'
sheet_name = 'DATA'

df = pd.read_excel(excel_file,
                   sheet_name=sheet_name,
                   usecols='A:I',
                   header=0)


df = df.replace(np.nan, '', regex=True)
df = df.groupby(by=['invoice_number', 'periode', 'bpr', 'tahun', 'bulan', 'status', 'harga', 'metode_pembayaran']).sum().reset_index()
df['bulan_number'] = df['bulan']
df['bulan'] = df['bulan'].apply(translate_bulan)
df['tahun'] = df['tahun'].astype(str)
df['invoice_number'] = df['invoice_number'].astype(str)

df_ori = df

# ## --- STREAMLIT SELECTION
periode = df['periode'].unique().tolist()
bpr_name = df['bpr'].unique().tolist()
tahun = df['tahun'].unique().tolist()
bulan = df['bulan'].unique().tolist()
status = df['status'].unique().tolist()
harga = df['harga'].unique().tolist()
metode_pembayaran = df['metode_pembayaran'].unique().tolist()

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
metode_pembayaran_selection = st.multiselect('Metode Pembayaran: ',
                                metode_pembayaran,
                                default=metode_pembayaran)

# --- FILTER DATAFRAME BASED ON SELECTION
mask = (df['status'].isin(status_selection) & 
        df['bulan'].isin(bulan_selection) &
        df['metode_pembayaran'].isin(metode_pembayaran_selection))

number_of_result = df[mask].shape[0]
st.markdown(f'*Hasil yang didapatkan: {number_of_result}*')

shw = df[mask].drop(columns=['bulan_number'])
st.dataframe(shw)


# --- GRAFIK PENDAPATAN
st.header('_Grafik Pendapatan_')
# multiple line by status
df = df[mask]
df['group_date'] = df['bulan'] + ' ' + df['tahun'].astype(str)
df_sorted = df.sort_values(by=['bulan_number', 'tahun'], ascending=True)
df_summary = df_sorted.groupby(['bulan_number', 'tahun', 'group_date', 'status'])['harga'].sum().reset_index()

shw = df_summary[mask].drop(columns=['bulan_number', 'tahun'])
st.dataframe(shw)

chart = px.line(df_summary, x='group_date', y='harga', color='status', text='harga', title='Total Pendapatan dalam Bulan - Tahun',
            labels={'harga': 'Total Harga', 'group_date': 'Bulan-Tahun'},
            line_shape="spline",
            color_discrete_map={'PAID': 'green', 'UNPAID': 'red', 'WAITING_PAYMENT': 'blue'}
        )
chart.update_yaxes(tickformat=",.0f", title="Total Harga")

# Tampilkan grafik menggunakan Streamlit
st.plotly_chart(chart)

# --- GRAFIK JUMLAH BY STATUS
st.header('_Grafik Jumlah BPR/S_')
df = df[mask]
df['group_date'] = df['bulan'] + ' ' + df['tahun'].astype(str)
df_sorted = df.sort_values(by=['bulan_number', 'tahun'], ascending=True)
df_summary = df_sorted.groupby(['bulan_number', 'tahun', 'group_date', 'status'])['bpr'].count().reset_index()

shw = df_summary[mask].drop(columns=['bulan_number', 'tahun'])
st.dataframe(shw)

chart = px.line(df_summary, x='group_date', y='bpr', color='status', text='bpr', title='Jumlah BPR/S dalam Bulan - Tahun',
            labels={'bpr': 'Jumlah BPR/S', 'group_date': 'Bulan-Tahun'},
            line_shape="spline",
            color_discrete_map={'PAID': 'green', 'UNPAID': 'red', 'WAITING_PAYMENT': 'blue'}
        )
chart.update_yaxes(tickformat=",.0f", title="Jumlah BPR/S")

# Tampilkan grafik menggunakan Streamlit
st.plotly_chart(chart)


# --- GRAFIK JUMLAH PENDAPATAN BY METODE PEMBAYARAN
st.header('_Grafik Berdasarkan Metode Pembayaran_')
df = df[mask]
mask = (df['status'].isin(['PAID']))
df = df[mask]

df['group_date'] = df['bulan'] + ' ' + df['tahun'].astype(str)
df_sorted = df.sort_values(by=['bulan_number', 'tahun'], ascending=True)

df_summary = df_sorted.groupby(['group_date', 'metode_pembayaran'])['harga'].sum().reset_index()

# shw = df_summary[mask].drop(columns=['bulan_number', 'tahun'])
st.dataframe(df_summary)
chart = px.line(df_summary, x='group_date', y='harga', color='metode_pembayaran', text='harga', title='Pendapatan Berdasarkan Metode Pembayaran dalam Bulan - Tahun',
            labels={'harga': 'Metode Pembayaran', 'group_date': 'Bulan-Tahun'},
            line_shape="spline",
            color_discrete_map={'MANDIRI PAYMENT': 'blue', 'FINNET/FINPAY': 'red'}
            
        )
chart.update_yaxes(tickformat=",.0f", title="Metode Pembayaran")

# Tampilkan grafik menggunakan Streamlit
st.plotly_chart(chart)


# --- DATA BPR NUNGGAK
st.header('_Data BPR/S Nunggak_')
st.markdown('_tidak terpengaruh filter diatas_')
df = df_ori
mask = (df['status'].isin(['UNPAID']))
df = df[mask]
# group by data bpr status unpaid lebih dari 1 dan di count jumlah nya
# saya ingin kolom nya bpr dan jumlah nunggak 
df['jumlah_tunggakan'] = df['bulan']
df_grouped = df.groupby(['bpr', 'status'])['jumlah_tunggakan'].count().reset_index()
st.dataframe(df_grouped)

# chart pie, dari jumlah tunggakan di atas di group lagi per jumlah tunggakan
df_grouped_by_jumlah = df_grouped.groupby(['jumlah_tunggakan'])['bpr'].count().reset_index()

pie_chart = px.pie(df_grouped_by_jumlah,
                title='Group By Jumlah Tunggakan',
                values='bpr',
                names='jumlah_tunggakan')
st.plotly_chart(pie_chart)