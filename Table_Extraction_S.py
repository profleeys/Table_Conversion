import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import base64

def create_download_link(data, filename):
    b64 = base64.b64encode(data).decode()  # 將檔案數據轉換為 base64 編碼
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64}" download="{filename}">點此下載</a>'
    return href

if __name__ == '__main__':
    st.title('資料轉換系統(html->xlsx)')

    file = st.file_uploader('請選擇要上傳的文件:', type=['html'])
    
    if file is not None:
        html_content = file.read().decode('utf-8')
        #st.warning(html_content[:300])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if col1.button('轉換檔案'):
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 找到所有的表格
        tables = soup.find_all('table')

        # 建立一個空的DataFrame
        combined_df = pd.DataFrame()

        # 逐個處理每個表格
        for table in tables:
            # 將表格轉換為DataFrame
            df = pd.read_html(str(table))[0]
            
            # 將DataFrame連接到combined_df
            combined_df = pd.concat([combined_df, df])

        # 將結果寫入Excel檔案
        combined_df.to_excel('converted.xlsx', index=False)
        
        #with open('converted.xlsx', 'rb') as f:
        #    data = f.read()

        #顯示下載連結
        #st.markdown(create_download_link(data, 'converted.xlsx'), unsafe_allow_html=True)
        
        with open('converted.xlsx', 'rb') as my_file:
            col2.download_button(label = '📥點此下載', data = my_file, file_name = 'converted.xlsx')    