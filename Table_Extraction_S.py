import streamlit as st
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import base64
import re

def create_download_link(data, filename):
    b64 = base64.b64encode(data).decode()  # 將檔案數據轉換為 base64 編碼
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64}" download="{filename}">點此下載</a>'
    return href

if __name__ == '__main__':
    st.title('資料轉換系統(html->xlsx)')

    file = st.file_uploader('請選擇要上傳的文件:', type=['html'])
    
    openF = False
    
    if file is not None:
        html_content = file.read().decode('utf-8')
        #st.warning(html_content[:300])
        openF = True
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if col1.button('轉換檔案') and openF == True:
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 找到所有的表格
        tables = soup.find_all('table')

        # 建立一個空的DataFrame
        combined_df = pd.DataFrame()

        extracted_city = 'Sheet1'

        # 逐個處理每個表格
        for table in tables:
            # 將表格轉換為DataFrame
            df = pd.read_html(str(table))[0]
            
            if df.shape[0] < 3:
                pattern = r'縣市別：(.*?) 製表日期'
                result = re.search(pattern, df.iloc[0][1][:100])
                if result:
                    extracted_city = result.group(1).replace(' ', '')
            else:
                # 檢查每個 row 中的每個欄位是否至少有一個數字
                #has_numeric_values = df.apply(lambda row: any(str(val).isdigit() or str(val) == '合 計' or str(val) == '申報大於歸戶' for val in row if pd.notnull(val)), axis=1)
                has_numeric_values = df.apply(lambda row: any(str(val).isdigit() for val in row if pd.notnull(val)), axis=1)

                # 保留至少有一個欄位的非空值為數字的資料
                df = df[has_numeric_values]
                
                # 將DataFrame連接到combined_df
                combined_df = pd.concat([combined_df, df])

        #combined_df = combined_df.drop(combined_df.index[0])  # 刪除第一個行
        combined_df = combined_df.drop(combined_df.columns[0], axis=1).reset_index(drop=True)  # 刪除第一個列

        combined_df.iloc[:, 0] = combined_df.iloc[:, 0].fillna(method='ffill', axis=0)
        
        split_index = combined_df.shape[0] // 2
        table1 = combined_df.iloc[:split_index, :-1]
        table2 = combined_df.iloc[split_index:, :-3]
        
        table1.columns = ['區鄉','里村','納稅單位','合計','營利所得','執行業務所得','薪資所得','利息所得','租賃及權利金','財產交易所得','機會中獎所得']
        table2.columns = ['區鄉','里村','股利所得','退職所得','其他所得','稿費所得','申報大於歸戶','薪資收入','稿費收入']

        # Perform a full outer join on columns 'A' and 'B'
        combined_df = pd.merge(table1, table2, on=['區鄉','里村'], how='outer')

        # 將結果寫入Excel檔案
        combined_df.to_excel('converted.xlsx', index=False, header=True, sheet_name=extracted_city)
        combined_df.to_csv('converted.csv', index=False, header=True)
        
        #with open('converted.xlsx', 'rb') as f:
        #    data = f.read()

        #顯示下載連結
        #st.markdown(create_download_link(data, 'converted.xlsx'), unsafe_allow_html=True)
        
        with open('converted.xlsx', 'rb') as my_file:
            col2.download_button(label = '📥點此下載', data = my_file, file_name = 'converted.xlsx')    