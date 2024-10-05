##############################################################
# Web App for removing background from an image   
#
# Author: tqye@yahoo.com
# History:
# When      | Who           | What
# 04/10/2024|TQ Ye          | Creation
##############################################################
import sys
import streamlit as st
from streamlit_javascript import st_javascript
from rembg import remove
import requests
from PIL import Image
import base64
import random
from random import randint
import io

class Local:    
    title: str
    choose_language: str
    language: str
    lang_code: str
    file_upload_label: str
    support_message: str
    
    def __init__(self, 
                title,
                choose_language,
                language,
                lang_code,
                file_upload_label,
                support_message,
                ):
        self.title= title
        self.choose_language = choose_language
        self.language= language
        self.lang_code= lang_code
        self.file_upload_label = file_upload_label
        self.support_message = support_message


en = Local(
    title="Remove Background",
    choose_language="选择界面语言",
    language="English",
    lang_code="en",
    file_upload_label="Please uploaded your image file (your file will never be saved anywhere)",
    support_message="Please report any issues or suggestions to tqye@yahoo.com",
)

zw = Local(
    title="图片去背景",
    choose_language="Choose UI Language",
    language="Chinese",
    lang_code="ch",
    file_upload_label="请上传你的图片文件（图片文件只在内存，不会被保留）",
    support_message="如遇什么问题或有什么建议，反馈，请电 tqye@yahoo.com",
)

def get_client_ip():
    '''
    workaround solution, via 'https://api.ipify.org?format=json' for get client ip
    example:
    ip_address = client_ip()  # now you have it in the host...
    st.write(ip_address)  # so you can log it, etc.    
    '''
    url = 'https://api.ipify.org?format=json'

    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')

    ip_address = ""
    try:
        result = st_javascript(script)
        if isinstance(result, dict) and 'ip' in result:
            ip_address = result['ip']
        else:
            ip_address = "unknown_ip"
    except:
        pass
        
    return ip_address

@st.cache_data()
def get_geolocation(ip_address):
    '''
    Get location of an IP address
    '''
    url =f'https://ipapi.co/{ip_address}/json/'

    try:
        # Make the GET requests
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        location = {
            "city" : data.get("city)"),
            "region" : data.get("region"),
            "country" : data.get("country_name"),
            }
        return location
    except requests.RequestException as ex:
        print(f"An error: {ex}")
        return None
    
def get_binary_file_downloader_html(bin_file : bytes, file_label='File'):
    '''
    Generates a link allowing the data in a given bin_file to be downloaded
    in:  bin_file (bytes)
    out: href string
    '''
    b64 = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">Download {file_label}</a>'
    
    return href

@st.cache_resource()
def Main_Title(text: str) -> None:

    st.markdown(f'<p style="background-color:#ffffff;color:#049ca4;font-weight:bold;font-size:24px;border-radius:2%;">{text}</p>', unsafe_allow_html=True)


##############################################
################ MAIN ########################
##############################################
def main(argv):
    
    Main_Title(st.session_state.locale.title + " (v0.0.1)")
    st.session_state.user_ip = get_client_ip()
    st.session_state.user_location = get_geolocation(st.session_state.user_ip)

    st.session_state.uploading_file_placeholder = st.empty()
    st.session_state.images_placeholder = st.empty()
    st.session_state.buttons_placeholder = st.empty()
    st.session_state.output_placeholder = st.empty()
    sendmail = True

    st.session_state.uploaded_file = st.session_state.uploading_file_placeholder.file_uploader(label=st.session_state.locale.file_upload_label, type=['png', 'jpg', 'jpeg'], key=st.session_state.fup_key)
    if st.session_state.uploaded_file is not None:
        with st.session_state.images_placeholder:
            input = Image.open(st.session_state.uploaded_file)
            with st.spinner('Wait ...'):
                new_img = remove(input)
            if isinstance(new_img, Image.Image):
                # display code: 2 column view
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Input Image")    
                    st.image(st.session_state.uploaded_file, width=300)
                with col2:
                    st.header("Output Image")
                    st.image(new_img, width=300)

                # create a download button
                with st.session_state.buttons_placeholder:
                    byte_arr = io.BytesIO()
                    new_img.save(byte_arr, format='PNG')
                    final_image_bytes = byte_arr.getvalue()
                    out_file_name = f"{st.session_state.uploaded_file.name.split('.')[0]}_nb.jpg"
                    st.markdown(get_binary_file_downloader_html(final_image_bytes, out_file_name), unsafe_allow_html=True)
                  
            else:
                st.image(st.session_state.uploaded_file, width=300)
                st.warning("Error: Failed to remove background")

    else:
        st.session_state.output_placeholder.warning("No file uploaded")


##############################
# Entry point
##############################
if __name__ == "__main__":

    # Initiaiise session_state elements
    if "locale" not in st.session_state:
        st.session_state.locale = zw

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    if "lang_index" not in st.session_state:
        st.session_state.lang_index = 1
        
    if "user_ip" not in st.session_state:
        st.session_state.user_ip = get_client_ip()

    if "user" not in st.session_state:
        st.session_state.user = "Anonymous"

    if 'fup_key' not in st.session_state:
        st.session_state.fup_key = str(random.randint(1000, 10000000))    
    
    st.markdown(
            """
                <style>
                    .appview-container .block-container {{
                        padding-top: {padding_top}rem;
                        padding-bottom: {padding_bottom}rem;
                    }}
                    .sidebar .sidebar-content {{
                        width: 200px;
                    }}
                    button {{
                        /*    height: auto; */
                        width: 120px;
                        height: 32px;
                        padding-top: 10px !important;
                        padding-bottom: 10px !important;
                    }}
                </style>""".format(padding_top=5, padding_bottom=10),
            unsafe_allow_html=True,
    )
        
    language = st.sidebar.selectbox(st.session_state.locale.choose_language, ("English", "中文"), index=st.session_state.lang_index)
    if language == "English":
        st.session_state.locale = en
        st.session_state.lang_index = 0
    else:
        st.session_state.locale = zw
        st.session_state.lang_index = 1

    st.sidebar.markdown(st.session_state.locale.support_message, unsafe_allow_html=True)
        
    main(sys.argv)


    
