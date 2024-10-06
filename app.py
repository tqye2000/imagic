###########################################################################
# Web App for removing background from an image   
#
# Author: tqye@yahoo.com
# History:
# When      | Who           | What
# 04/10/2024|TQ Ye          | Creation
# 06/10/2024|TQ Ye          | Allow selecting differnt model and
#           |               | setting the output background colour
############################################################################
import sys
import streamlit as st
from streamlit_javascript import st_javascript
from rembg import remove, new_session
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
    choose_model_prompt: str
    choose_color_prompt: str
    file_upload_label: str
    file_download_label: str
    support_message: str
    
    def __init__(self, 
                title,
                choose_language,
                language,
                lang_code,
                choose_model_prompt,
                choose_color_prompt,
                file_upload_label,
                file_download_label,
                support_message,
                ):
        self.title= title
        self.choose_language = choose_language
        self.language= language
        self.lang_code= lang_code
        self.choose_model_prompt=choose_model_prompt
        self.choose_color_prompt=choose_color_prompt
        self.file_upload_label = file_upload_label
        self.file_download_label=file_download_label
        self.support_message = support_message


en = Local(
    title="Remove Background",
    choose_language="选择界面语言",
    language="English",
    lang_code="en",
    choose_model_prompt="Choose which model to use",
    choose_color_prompt="Choose background colour",
    file_upload_label="Please uploaded your image file (your file will never be saved anywhere)",
    file_download_label="Download",
    support_message="Please report any issues or suggestions to tqye@yahoo.com",
)

zw = Local(
    title="图片去背景",
    choose_language="Choose UI Language",
    language="Chinese",
    lang_code="ch",
    choose_model_prompt="选择模型",
    choose_color_prompt="选择输出背景色。空缺为无色",
    file_upload_label="请上传你的图片文件（图片文件只在内存，不会被保留）",
    file_download_label="下载链接",
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
    
def enable_bgcolour():

    st.session_state.disabled = not st.session_state.disabled

def get_binary_file_downloader_html(bin_file : bytes, file_label='File'):
    '''
    Generates a link allowing the data in a given bin_file to be downloaded
    in:  bin_file (bytes)
    out: href string
    '''
    b64 = base64.b64encode(bin_file).decode()
    href = f'{st.session_state.locale.file_download_label} <a href="data:application/octet-stream;base64,{b64}" download="{file_label}">{file_label}</a>'

    return href

@st.cache_resource()
def Main_Title(text: str) -> None:

    st.markdown(f'<p style="background-color:#ffffff;color:#049ca4;font-weight:bold;font-size:24px;border-radius:2%;">{text}</p>', unsafe_allow_html=True)


##############################################
################ MAIN ########################
##############################################
def main(argv):
    
    Main_Title(st.session_state.locale.title + " (v0.0.2)")
    st.session_state.user_ip = get_client_ip()
    st.session_state.user_location = get_geolocation(st.session_state.user_ip)
    
    st.session_state.model_select_placeholder = st.empty()
    st.session_state.bgcolour_select_placeholder = st.empty()
    st.session_state.uploading_file_placeholder = st.empty()
    st.session_state.images_placeholder = st.empty()
    st.session_state.buttons_placeholder = st.empty()
    st.session_state.output_placeholder = st.empty()

    with st.session_state.model_select_placeholder:
        st.session_state.model_name = st.selectbox(label=st.session_state.locale.choose_model_prompt, options=("isnet-general-use", "u2net",))
        st.session_state.rembg_session = new_session(st.session_state.model_name)

    with st.session_state.bgcolour_select_placeholder:
        col1, col2 = st.columns(2)
        bgcolour_enable = col1.checkbox(label=st.session_state.locale.choose_color_prompt, on_change=enable_bgcolour)
        if bgcolour_enable:
            st.session_state.bg_color_hex = col2.color_picker(label="colour", disabled=st.session_state.disabled, value="#002200")
            # Convert color hex string to (R, G, B)
            bg_color_rgb = tuple(int(st.session_state.bg_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            st.session_state.bg_color = bg_color_rgb + (255,)  # Add alpha channel for RGBA
        else:
            st.session_state.bg_color = None

    st.session_state.uploaded_file = st.session_state.uploading_file_placeholder.file_uploader(label=st.session_state.locale.file_upload_label, type=['png', 'jpg', 'jpeg'], key=st.session_state.fup_key)
    if st.session_state.uploaded_file is not None:
        with st.session_state.images_placeholder:
            input_img = Image.open(st.session_state.uploaded_file)      #input_img: PIL image
            with st.spinner('Wait ...'):
                new_img = remove(input_img, bgcolor=st.session_state.bg_color, session=st.session_state.rembg_session)                             #new_img: PIL image
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
        
    if "model_name" not in st.session_state:
        st.session_state.model_name = "isnet-general-use"
        
    if "rembg_session" not in st.session_state:
        st.session_state.rembg_session = new_session(st.session_state.model_name)

    if "bg_color_hex" not in st.session_state:
        st.session_state.bg_color_hex = "#002200"

    if "bg_color" not in st.session_state:
        st.session_state.bg_color = None

    if "disabled" not in st.session_state:
        st.session_state.disabled = True

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


    
