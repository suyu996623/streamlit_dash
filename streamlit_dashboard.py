import pandas as pd
import streamlit as st

st.set_page_config(
    page_title='2x2 Tidy Data 薪資儀表板', layout='wide'
)

# 1. 載入並處理資料
@st.cache_data
def get_tidy_2x2():
    df_2x2 = pd.read_excel(
        'Chapter4_raw_data_01.xlsx', sheet_name='2x2', header=[0, 1]
    )
    df_2x2.columns = [
        col[1] if 'Unnamed:' in str(col[0]) else f'{col[0]}_{col[1]}'
        for col in df_2x2.columns
    ]
    df_2x2['地區'] = df_2x2['地區'].ffill()
    tidy_2x2 = df_2x2.melt(
        id_vars=['地區', '產業類別'], var_name='部門_職務', value_name='薪資'
    )
    tidy_2x2[['部門', '職務']] = tidy_2x2['部門_職務'].str.split(
        '_', expand=True
    )
    tidy_2x2.drop(columns=['部門_職務'], inplace=True)
    tidy_2x2['薪資'] = pd.to_numeric(tidy_2x2['薪資'])
    return tidy_2x2


tidy_2x2 = get_tidy_2x2()

st.title('📊 2x2 Tidy Data 薪資多維度篩選儀表板')

# 2. 側邊欄複選篩選器
st.sidebar.header('🔍 變數多重篩選')
regions = st.sidebar.multiselect(
    '地區',
    tidy_2x2['地區'].unique(),
    default=tidy_2x2['地區'].unique(),
)
industries = st.sidebar.multiselect(
    '產業類別',
    tidy_2x2['產業類別'].unique(),
    default=tidy_2x2['產業類別'].unique(),
)
depts = st.sidebar.multiselect(
    '部門',
    tidy_2x2['部門'].unique(),
    default=tidy_2x2['部門'].unique(),
)
positions = st.sidebar.multiselect(
    '職務',
    tidy_2x2['職務'].unique(),
    default=tidy_2x2['職務'].unique(),
)

# 資料過濾
filtered = tidy_2x2[
    (tidy_2x2['地區'].isin(regions))
    & (tidy_2x2['產業類別'].isin(industries))
    & (tidy_2x2['部門'].isin(depts))
    & (tidy_2x2['職務'].isin(positions))
]

# 3. KPI 指標顯示
c1, c2, c3, c4 = st.columns(4)
c1.metric('篩選總筆數', f'{len(filtered):,} 筆')
c2.metric(
    '平均薪資',
    f"${filtered['薪資'].mean():,.0f}" if not filtered.empty else '$0',
)
c3.metric(
    '最高薪資',
    f"${filtered['薪資'].max():,.0f}" if not filtered.empty else '$0',
)
c4.metric(
    '最低薪資',
    f"${filtered['薪資'].min():,.0f}" if not filtered.empty else '$0',
)

st.markdown('---')

# 4. 圖表與明細表
col_chart, col_table = st.columns([1, 1])

with col_chart:
    st.subheader('📈 薪資分組統計圖')
    group_dim = st.selectbox('選擇分組維度', ['地區', '產業類別', '部門', '職務'])
    if not filtered.empty:
        chart_data = (
            filtered.groupby(group_dim)['薪資'].mean().reset_index()
        )
        st.bar_chart(chart_data.set_index(group_dim))
    else:
        st.warning('無資料可繪製圖表')

with col_table:
    st.subheader('📋 篩選後明細')
    st.dataframe(
        filtered[['地區', '產業類別', '部門', '職務', '薪資']],
        use_container_width=True,
        height=380,
    )