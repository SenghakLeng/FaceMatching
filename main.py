import streamlit as st
from deepface import DeepFace
from streamlit_option_menu import option_menu
import os
from PIL import Image
import cv2
import numpy as np
import shutil
from fixOrientaion import fixImage



def draw_box_on_img(img, bbox, ver_stat):
    x, y, w, h = bbox
    # Draw the bounding box rectangle on the image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if ver_stat:
        color = (0,255,0)
    else: 
        color = (255, 0, 0)
    image_np = cv2.rectangle(img, (x, y), (x+w, y+h), color=color, thickness=3)

    # Convert the image back to PIL format
    image_pil = Image.fromarray(image_np)

    return image_pil.resize((640, 640))

def face_recognition(img1, img2):
    
    image1 = np.array(fixImage(img1))
    image2 = np.array(fixImage(img2))
    
    image1 = cv2.cvtColor(image1, cv2.COLOR_RGBA2BGR)
    image2 = cv2.cvtColor(image2, cv2.COLOR_RGBA2BGR)
    try:
        verification_result = DeepFace.verify(img1_path=image1, img2_path= image2, 
                                            detector_backend='mtcnn',
                                            model_name='ArcFace')
        verify_stat = verification_result['verified']

        img1_box_x = verification_result['facial_areas']['img1']['x']
        img1_box_y = verification_result['facial_areas']['img1']['y']
        img1_box_w = verification_result['facial_areas']['img1']['w']
        img1_box_h = verification_result['facial_areas']['img1']['h']

        img2_box_x = verification_result['facial_areas']['img2']['x']
        img2_box_y = verification_result['facial_areas']['img2']['y']
        img2_box_w = verification_result['facial_areas']['img2']['w']
        img2_box_h = verification_result['facial_areas']['img2']['h']

        img1_box = [img1_box_x, img1_box_y, img1_box_w, img1_box_h]
        img2_box = [img2_box_x, img2_box_y, img2_box_w, img2_box_h]

        draw_img1 = draw_box_on_img(np.array(image1), img1_box, ver_stat=verify_stat)
        draw_img2 = draw_box_on_img(np.array(image2), img2_box, ver_stat= verify_stat)

        return draw_img1, draw_img2, verify_stat
    
    except ValueError as e:
        st.error('The face is not detected correctly!!! Please check the alignment and try again!')
    except Exception as e:
        st.error("Error: {}".format(str(e)))
    

    

def database_page():
    st.header('This is the database')
 

    tab1, tab2 = st.tabs(['Database images', 'Upload images to the database'])
    with tab2:
        images = st.file_uploader('Upload images to the databse', accept_multiple_files= True,
                                type=['jpg', 'jpeg', 'png'])
        if images is not None:
            for im in images:
                upload_img = fixImage(im).convert("RGB")
                upload_img.save(os.path.join('./database_img', im.name))
    with tab1:
        directory = './database_img'
        image_files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        num_columns = 3

        for i in range(0, len(image_files), num_columns):
            col1, col2, col3 = st.columns(num_columns)
            for j, col in enumerate([col1, col2, col3]):
                if i + j < len(image_files):
                    image_path = os.path.join(directory, image_files[i + j])
                    image = Image.open(image_path)
                    col.image(image, use_column_width=True, caption=image_files[i + j])
                else:
                    col.empty()
        
        colu = st.columns(5)
        with colu[2]:
            if st.button(label="Remove all"):
                shutil.rmtree('./database_img')
                os.mkdir('./database_img')





def verifcation_page(drawed_img1, drawed_img2, verification_stat):
    st.subheader('This is the verification results...')
    col1, col2 = st.columns(2)
    with col1:
        st.image(drawed_img1, caption='This is your referenced images')
    with col2:
        st.image(drawed_img2, caption= 'This is your test image')
    ncol1, ncol2, ncol3 = st.columns(3)
    if verification_stat:
        with ncol2:
            st.markdown("<h1 style='text-align: center; font-size: 30px; \
                        color: green;'>Verification Success!!!</h1>", 
                        unsafe_allow_html=True)
    else: 
        with ncol2:
            st.markdown("<h1 style='text-align: center; font-size: 30px; \
                        color: red;'>Face unmatched!!!</h1>", 
                        unsafe_allow_html=True)

def top_page_stateless():
    col1, col2 = st.columns([9,1])
    with col1: 
        st.title('AI Face Matching Demo')
    with col2:
        st.image('./logo.png', width=80)
    st.markdown("\n\n")
    st.caption('This is a demo where you can test the faces between 2 individuals and show if it is the same person')
    with st.sidebar:
        selected = option_menu(
            menu_title = 'Main Menu',
            options = ['Test between 2 images',
                       'Test image with database',
                       'Database images',
                       'Setting'],
            icons= ['images', 'database-fill-check', 'database', 'gear'],
            menu_icon='list',
            default_index= 0,
        )
    st.markdown(
        """
        <style>
        div[class="fullScreenFrame"] > div[data-testid="stHorizontalBlock"] {
            margin-top: -50px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    return selected

def test_2_img_page():
    st.subheader('Test between 2 images to see if it is the same person')
    tab1, tab2 = st.tabs(['Upload from local file', 'Take a photo'])
    with tab1:
        t1col1, t1col2 = st.columns(2)
        with t1col1:
            t1img1 = st.file_uploader('Upload your reference image...',accept_multiple_files= False, 
                                      type = ['jpg', 'jpeg', 'png'])
            if t1img1 is not None:
                st.image(fixImage(t1img1), caption= 'This is your reference image')
                # st.write(t1img1)
        with t1col2: 
            t1img2 = st.file_uploader('Upload your test image...',accept_multiple_files= False, 
                                      type = ['jpg', 'jpeg', 'png'],)
            if t1img2 is not None:
                st.image(fixImage(t1img2), caption= 'This is your input image')
        if (t1img1 is not None) and (t1img2 is not None):
            try:
                newimg1, newimg2, verification_stat = face_recognition(t1img1, t1img2)
                verifcation_page(drawed_img1=newimg1, drawed_img2=newimg2, verification_stat=verification_stat)
            except Exception:
                pass


    with tab2:
        t2col1, t2col2 = st.columns(2)
        with t2col1:
            t2img1 =  st.file_uploader('Upload your reference image..',accept_multiple_files= False, 
                                      type = ['jpg', 'jpeg', 'png'])
            if t2img1 is not None:
                st.image(fixImage(t2img1), caption= 'This is your reference image')
        with t2col2:
            t2img2 = st.camera_input('Take a photo to verify image')
            if t2img2 is not None:
                st.image(fixImage(t2img2), caption = 'This is your captured image')
        if (t2img1 is not None) and (t2img2 is not None):
            try: 
                newimg1, newimg2, verification_stat = face_recognition(t2img1, t2img2)
                verifcation_page(drawed_img1=newimg1, drawed_img2=newimg2, verification_stat=verification_stat)
            except Exception:
                pass
    
def test_img_database_page():
    st.subheader('This is to check between the input image and database image')
    tab1, tab2 = st.tabs(['Upload from local file', 'Take a photo'])
    with tab1:
        img_up = st.file_uploader('Upload your test image here...', type= ['jpg', 'jpeg', 'png'], 
                            accept_multiple_files=False)
        ncol1, ncol2, ncol3 = st.columns(3)
        with ncol2:
            if img_up is not None:
                st.image(fixImage(img_up), caption='This is your test image')
        if len(os.listdir('./database_img/')) > 0:
            try:
                for f in os.listdir('./database_img'):
                    data_img_path = os.path.join('./database_img', f)
                    
                    drawim1, drawim2, ver_state = face_recognition(data_img_path,img_up)
                    if ver_state:
                        existed_in_data = True
                        draw_image1 = drawim1
                        draw_image2 = drawim2
                        break
                    else:
                        existed_in_data = False
                if existed_in_data:
                    verifcation_page( drawed_img1=draw_image1, drawed_img2=draw_image2, verification_stat= ver_state)
                else: 
                    st.error('\tThis person is unrecognized', icon="❌")
            except Exception:
                pass
        else:
            st.markdown("<h1 style='text-align: center; font-size: 30px; \
                        color:red;'>There is no image in the database!!!</h1>", 
                        unsafe_allow_html=True)
                    
    with tab2:
        img_cam = st.camera_input('Take a photo to check with database')
        ncol1, ncol2, ncol3 = st.columns(3)
        with ncol2:
            if img_cam is not None:
                if len(os.listdir('./database_img/')) > 0:
                    try: 
                        for f in os.listdir('./database_img'):
                            img_path = os.path.join('./database_img', f)
                            drawim1, drawim2, ver_state = face_recognition(img_path, img_cam)
                            if ver_state:
                                existed_in_data = True
                                draw_image1 = drawim1
                                draw_image2 = drawim2
                                break
                            else:
                                existed_in_data = False
                        if existed_in_data:
                            verifcation_page( drawed_img1=draw_image1, drawed_img2=draw_image2, verification_stat= ver_state)
                        else: 
                            st.error('\tThis person is unrecognized', icon="❌")
                    except Exception:
                        pass
                else:
                    st.markdown("<h1 style='text-align: center; font-size: 30px; \
                                color:red;'>There is no image in the database!!!</h1>", 
                                unsafe_allow_html=True)

def setting_page():
    st.header('There is nothing here yet!')

def main():
    database_path = './database_img' 
    if os.path.exists(database_path):
        pass
    else:
        os.mkdir(database_path)
    
    st.set_page_config(
    page_title="AI Face Matching Demo",
    layout="wide",
    initial_sidebar_state="expanded"
    )
    hide = """
    <style>
        .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
        .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
        .viewerBadge_text__1JaDK {
        display: none;
        }
        # footer { visibility: hidden; } 
        header { visibility: hidden; }
        #MainMenu {visibility: visible;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide, unsafe_allow_html=True)
    selected = top_page_stateless()
    if selected == 'Test between 2 images':
        test_2_img_page() 
    elif selected == 'Test image with database':
        test_img_database_page()
    elif selected == 'Database images':
        database_page()
    elif selected == 'Setting':
        setting_page()
        
    
if __name__ == "__main__":
    main()
