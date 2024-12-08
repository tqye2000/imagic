###############################################################################
# Web App for image enhancement
#
# Author: tqye@yahoo.com
# History:
# When      | Who           | What
# 04/10/2024|TQ Ye          | Creation
# 06/10/2024|TQ Ye          | Allow selecting differnt model and
#           |               | setting the output background colour
# 07/10/2024|TQ Ye          | Add image enhancement option
# 11/10/2024|TQ Ye          | Allow user to adjust image enhancement parameters
# 06/12/2024|TQ Ye          | Further improvement for portrait enhancement
###############################################################################
import sys
import streamlit as st
from streamlit_javascript import st_javascript
from rembg import remove, new_session
from PIL import Image, ImageEnhance, ImageFilter
#import mediapipe as mp
import cv2
import requests
import numpy as np
import base64
import random
from random import randint
import io

class Local:    
    title: str
    choose_language: str
    language: str
    lang_code: str
    choose_proccess_prompt: str
    choose_model_prompt: str
    choose_color_prompt: str
    image_enhance_label: str
    image_remove_bg_label: str
    advanced_setting_label: str
    is_portrait_Label: str
    smooth_skin_Label: str
    smooth_skin_prompt: str
    enhance_eyes_Label: str
    file_upload_label: str
    file_download_label: str
    support_message: str
    
    def __init__(self, 
                title,
                choose_language,
                language,
                lang_code,
                choose_proccess_prompt,
                choose_model_prompt,
                choose_color_prompt,
                image_enhance_label,
                image_remove_bg_label,
                advanced_setting_label,
                is_portrait_Label,
                smooth_skin_Label,
                smooth_skin_prompt,
                enhance_eyes_Label,
                file_upload_label,
                file_download_label,
                support_message,
                ):
        self.title= title
        self.choose_language = choose_language
        self.language= language
        self.lang_code= lang_code
        self.lang_code= lang_code
        self.choose_proccess_prompt=choose_proccess_prompt
        self.choose_model_prompt=choose_model_prompt
        self.choose_color_prompt=choose_color_prompt
        self.image_enhance_label = image_enhance_label
        self.image_remove_bg_label = image_remove_bg_label
        self.advanced_setting_label = advanced_setting_label
        self.is_portrait_Label = is_portrait_Label
        self.smooth_skin_Label = smooth_skin_Label
        self.smooth_skin_prompt = smooth_skin_prompt
        self.enhance_eyes_Label = enhance_eyes_Label
        self.file_upload_label = file_upload_label
        self.file_download_label=file_download_label
        self.support_message = support_message

en = Local(
    title="Image Processing",
    choose_language="选择界面语言",
    language="English",
    lang_code="en",
    choose_proccess_prompt="Choose the process",
    choose_model_prompt="Choose which model to use",
    choose_color_prompt="Choose background colour",
    image_enhance_label="Image Enhancement",
    image_remove_bg_label="Remove Background",
    advanced_setting_label="Adjust Parameters",
    is_portrait_Label="Is it a Portrait?",
    smooth_skin_Label="Smooth Skin",
    smooth_skin_prompt="Enable for portraits to smooth skin texture",
    enhance_eyes_Label="Enhance eyes for portraits",
    file_upload_label="Please uploaded your image file (your file will never be saved anywhere)",
    file_download_label="Download",
    support_message="Please report any issues or suggestions to tqye@yahoo.com",
)

zw = Local(
    title="处理图片",
    choose_language="Choose UI Language",
    language="Chinese",
    lang_code="ch",
    choose_proccess_prompt="选择处理方式",
    choose_model_prompt="选择模型",
    choose_color_prompt="选择输出背景色。空缺为无色",
    image_enhance_label="图片增强",
    image_remove_bg_label="去除背景",
    advanced_setting_label="调整参数",
    is_portrait_Label="人物肖像",
    smooth_skin_Label="柔化皮肤",
    smooth_skin_prompt="处理人物肖像，请选择这个选项！否则不选。",
    enhance_eyes_Label="强化眼睛",
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

    return sender_email, password

def model_changed():
    st.session_state.rembg_session = new_session(st.session_state.model_name)

def enable_bgcolour():
    st.session_state.disabled = not st.session_state.disabled

# def is_portrait(image: Image) -> bool:
#     # Initialize MediaPipe Face Detection
#     mp_face_detection = mp.solutions.face_detection
#     face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

#     # Convert PIL Image to OpenCV format (BGR)
#     image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

#     # Detect faces
#     results = face_detection.process(image_cv)

#     # Check if any faces were detected
#     return bool(results.detections)

def enhance_eyes(img: Image) -> Image:
    '''
    Enhance eyes by increasing local contrast and clarity.
    Without AI-based facial detection, we'll need to use general image processing techniques 
    that hopefully enhance the eye regions' contrast and clarity.
    '''
    # Convert to LAB color space for better control
    from skimage import color
    import numpy as np
    
    # Convert PIL to numpy array
    img_np = np.array(img)
    
    # Convert to LAB color space
    lab = color.rgb2lab(img_np / 255.0)
    
    # Increase lightness contrast
    L = lab[:, :, 0]
    L = np.clip(L * 1.2, 0, 100)  # Increase contrast of lightness channel
    lab[:, :, 0] = L
    
    # Convert back to RGB
    enhanced = color.lab2rgb(lab) * 255.0
    enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
    
    # Convert back to PIL Image
    return Image.fromarray(enhanced)

def image_enhancement(img: Image) -> Image:
    '''
    This function is used to enhance the image
    in:  img (PIL image)
    out: img (PIL image)
    '''
    # Convert to RGB if image is in RGBA mode
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Step 0: Noise Reduction (apply before enhancements)
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # Step 1: Color Correction
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(st.session_state.color)  # Increase color saturation by 10%

    # Step 2: Selective smoothing (good for portraits)
    if st.session_state.smooth_skin:  # Add this checkbox to your UI
        smooth_img = img.filter(ImageFilter.SMOOTH_MORE)
        # Blend smoothed version with original to maintain some texture
        img = Image.blend(img, smooth_img, 0.6)  # 60% smooth, 40% original

    # Eye enhancement (if enabled)
    if st.session_state.enhance_eyes:
        # Create a copy for eye enhancement
        eye_enhanced = enhance_eyes(img)
        # Blend the eye-enhanced version with original
        img = Image.blend(img, eye_enhanced, st.session_state.eye_strength)
        
        #img = enhance_portrait(img)

	# Step 3: Brightness Enhancement
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(st.session_state.brightness)  # Increase brightness by 10%

	# Step 4: Contrast Enhancement (after brightness)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(st.session_state.contrast)  # Increase contrast by 30%

    # Step 5: Sharpness Enhancement
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(st.session_state.sharpness)  # Increase sharpness by 10%
 
    # Step 5: Teeth Whitening (assuming teeth are a specific region)
    # This step would also require more complex image processing to identify and whiten teeth
 
    # Step 6: Background Blur
    #img = img.filter(ImageFilter.GaussianBlur(radius=st.session_state.blur))

    # Step 6: Smart Sharpening
    if st.session_state.sharpness > 1.0:
        # Use UnsharpMask for more controlled sharpening
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        if st.session_state.sharpness > 1.5:
            # Additional edge enhancement for higher sharpness values
            img = img.filter(ImageFilter.EDGE_ENHANCE)
    
    return img

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
    
    Main_Title(st.session_state.locale.title + " (v0.0.4)")
    st.session_state.user_ip = get_client_ip()
    st.session_state.user_location = get_geolocation(st.session_state.user_ip)

    st.session_state.proccess_select_placeholder = st.empty()

    st.session_state.model_select_placeholder = st.empty()
    st.session_state.is_portrait_placeholder = st.empty()
    st.session_state.bgcolour_select_placeholder = st.empty()
    st.session_state.uploading_file_placeholder = st.empty()
    st.session_state.images_placeholder = st.empty()
    st.session_state.buttons_placeholder = st.empty()
    st.session_state.output_placeholder = st.empty()

    with st.session_state.proccess_select_placeholder:
        st.session_state.process_name = st.selectbox(label=st.session_state.locale.choose_proccess_prompt, options=(st.session_state.locale.image_enhance_label, st.session_state.locale.image_remove_bg_label,))
        if st.session_state.process_name == st.session_state.locale.image_remove_bg_label:
            #remove background
            with st.session_state.model_select_placeholder:
                st.session_state.model_name = st.selectbox(label=st.session_state.locale.choose_model_prompt, options=("isnet-general-use", "u2net",))
                st.session_state.rembg_session = new_session(st.session_state.model_name)
            with st.session_state.bgcolour_select_placeholder:
                col1, col2 = st.columns(2)
                bgcolour_enable = col1.checkbox(label=st.session_state.locale.choose_color_prompt, on_change=enable_bgcolour)
                if bgcolour_enable:
                    col2.color_picker(label="colour", disabled=st.session_state.disabled, value=st.session_state.bg_color_hex, key="bg_color_hex")
                    # Convert color hex string to (R, G, B)
                    bg_color_rgb = tuple(int(st.session_state.bg_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    st.session_state.bg_color = bg_color_rgb + (255,)  # Add alpha channel for RGBA
                else:
                    st.session_state.bg_color = None
        else:
            #image enhancement
            st.session_state.is_portrait_placeholder.checkbox(st.session_state.locale.is_portrait_Label, key="is_portrait", help=st.session_state.locale.smooth_skin_prompt)
            with st.session_state.bgcolour_select_placeholder:
                with st.expander(st.session_state.locale.advanced_setting_label):
                    en_col1, en_col2 = st.columns(2)
                    #en_col1.checkbox(st.session_state.locale.smooth_skin_Label, key="smooth_skin", help=st.session_state.locale.smooth_skin_prompt)
                    #en_col2.checkbox("Enhance Eyes", key="enhance_eyes", help="Enhance eye clarity and contrast")
                    #st.session_state.smooth_skin = en_col1.checkbox(st.session_state.locale.smooth_skin_Label, value=st.session_state.smooth_skin, help=st.session_state.locale.smooth_skin_prompt)
                    #st.session_state.enhance_eyes = en_col1.checkbox(st.session_state.locale.enhance_eyes_Label, value=st.session_state.enhance_eyes, help="Enhance eye clarity and contrast")
                    #en_col2.slider("Eye Enhancement Strength", 0.0, 1.0, key="eye_strength", value=0.2, disabled=st.session_state.enhance_eyes)   #slider for blur

                    #slider for color
                    en_col1.slider("Color", 0.0, 2.0, key="color", value=st.session_state.color)
                    #slider for brightness
                    en_col2.slider("Brightness", 0.5, 2.0, key="brightness", value=st.session_state.brightness)
                    #slider for contrast
                    en_col1.slider("Contrast", 0.5, 2.0, key="contract", value=st.session_state.contrast)
                    #slider for sharpness
                    en_col2.slider("Sharpness", 0.0, 2.0, key="sharpness", value=st.session_state.sharpness)
                    #st.session_state.blur = en_col2.slider("Background Blur", 1, 4, 2)
                    #slider for noise
                    #st.session_state.noise = en_col2.slider("Noise Reduction", 1, 4, 3)

    st.session_state.uploaded_file = st.session_state.uploading_file_placeholder.file_uploader(label=st.session_state.locale.file_upload_label, type=['png', 'jpg', 'jpeg'], key=st.session_state.fup_key)
    if st.session_state.uploaded_file is not None:
        with st.session_state.images_placeholder:
            input_img = Image.open(st.session_state.uploaded_file)      #input_img: PIL image
            with st.spinner('Wait ...'):
                if st.session_state.process_name == st.session_state.locale.image_enhance_label:
                    st.session_state.smooth_skin = st.session_state.is_portrait
                    st.session_state.enhance_eyes = st.session_state.is_portrait
                    new_img = image_enhancement(input_img)
                else:
                    new_img = remove(input_img, bgcolor=st.session_state.bg_color, session=st.session_state.rembg_session)                             #new_img: PIL image
        
            # Check if the image was successfully processed
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
                    if st.session_state.process_name == st.session_state.locale.image_enhance_label:
                        out_file_name = f"{st.session_state.uploaded_file.name.split('.')[0]}_enhanced.jpg"
                    else:
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
        st.session_state.model_name = "isnet-general-use"  # "u2net" 
        
    if "rembg_session" not in st.session_state:
        st.session_state.rembg_session = new_session(st.session_state.model_name)

    if "bg_color_hex" not in st.session_state:
        st.session_state.bg_color_hex = "#002200"

    if "bg_color" not in st.session_state:
        st.session_state.bg_color = None

    if "color" not in st.session_state:
        st.session_state.color = 1.2    # Increase color saturation by 20%

    if "contrast" not in st.session_state:
        st.session_state.contrast = 1.1   # Increase contrast by 10%

    if "brightness" not in st.session_state:
        st.session_state.brightness = 1.1   # Increase brightness by 10%

    if "sharpness" not in st.session_state:
        st.session_state.sharpness = 1.2

    if "is_portrait" not in st.session_state:
        st.session_state.is_portrait = True

    if "smooth_skin" not in st.session_state:
        st.session_state.smooth_skin = True

    if "enhance_eyes" not in st.session_state:
        st.session_state.enhance_eyes = True
        
    if "eye_strength" not in st.session_state:
        st.session_state.eye_strength = 0.25  # 30% blend by default

    if "blur" not in st.session_state:
        st.session_state.blur = 2       # kernel size in pixels

    if "noise" not in st.session_state:
        st.session_state.noise = 3      # Standard deviation of the Gaussian kernel

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


    
