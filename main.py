import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import random
import zipfile

st.title('Image Text Adder with Random Numbers')

# Input list of names
nameTile = st.text_input('Enter names separated by commas', 'AAA,BBB,CCC')
names = nameTile.split(',')

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and names:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    st.write("")
    st.write("Add random number text to your image:")

    if 'random_numbers' not in st.session_state:
        st.session_state.random_numbers = []

    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    # Initialize session state to store multiple texts
    if 'texts' not in st.session_state:
        st.session_state.texts = []

    # Add new text item with random number
    if st.button('Add Random Number Text'):
        random_number = random.randint(0, 9999)
        st.session_state.texts.append({'text': str(random_number), 'x': 10, 'y': 10, 'font_size': 20})

    # Layout for text selection and editing
    if st.session_state.texts:
        selected_text_index = st.selectbox(
            "Select text to edit",
            options=list(range(len(st.session_state.texts))),
            format_func=lambda x: f"Text {x + 1}"
        )

        if selected_text_index is not None:
            text_item = st.session_state.texts[selected_text_index]
            
            # Grouping sliders into columns for better layout
            col1, col2 = st.columns(2)
            with col1:
                text_item['x'] = st.slider(f"X Position {selected_text_index + 1}", 0, image.width, text_item['x'], key=f"x_{selected_text_index}")
            with col2:
                text_item['y'] = st.slider(f"Y Position {selected_text_index + 1}", 0, image.height, text_item['y'], key=f"y_{selected_text_index}")
            col3, col4 = st.columns(2)
            with col3:
                text_item['font_size'] = st.slider(f"Font Size {selected_text_index + 1}", 10, 100, text_item['font_size'], key=f"font_{selected_text_index}")

    st.write("")

    # Generate Random Numbers button
    st.button('Generate Random Numbers', on_click=lambda: setattr(st.session_state, 'random_numbers', random.sample(range(1000), len(names) * len(st.session_state.texts))))

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Previous'):
            st.session_state.current_index = (st.session_state.current_index - 1) % len(names)
    with col3:
        if st.button('Next'):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(names)

    st.write("")

    # Controls for nameTile position and font size
    st.subheader("NameTile Settings")
    name_col1, name_col2 = st.columns(2)
    with name_col1:
        name_x = st.slider("X Position for NameTile", 0, image.width, 10)
    with name_col2:
        name_y = st.slider("Y Position for NameTile", 0, image.height, 10)
    name_col3, name_col4 = st.columns(2)
    with name_col3:
        name_font_size = st.slider("Font Size for NameTile", 10, 100, 20)

    if st.session_state.random_numbers:
        current_index = st.session_state.current_index

        # Create an editable image
        edited_image = image.copy()
        draw = ImageDraw.Draw(edited_image)
        random_numbers_for_current_image = st.session_state.random_numbers[current_index * len(st.session_state.texts):(current_index + 1) * len(st.session_state.texts)]
        for i, text_item in enumerate(st.session_state.texts):
            font = ImageFont.truetype("UID LETTER.ttf", text_item['font_size'])
            draw.text((text_item['x'], text_item['y']), str(random_numbers_for_current_image[i]), font=font, fill="white")
        
        # Add nameTile text
        name_tile_text = names[current_index]
        font = ImageFont.truetype("UID LETTER.ttf", name_font_size)
        draw.text((name_x, name_y), name_tile_text, font=font, fill="white")
        
        st.image(edited_image, caption=f'Edited Image {names[current_index]}', use_column_width=True)
        
        # Save the edited image
        img_byte_arr = io.BytesIO()
        edited_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Create a ZIP file containing all images
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, name in enumerate(names):
                temp_image = image.copy()
                draw = ImageDraw.Draw(temp_image)
                random_numbers_for_image = st.session_state.random_numbers[i * len(st.session_state.texts):(i + 1) * len(st.session_state.texts)]
                for j, text_item in enumerate(st.session_state.texts):
                    font = ImageFont.truetype("UID LETTER.ttf", text_item['font_size'])
                    draw.text((text_item['x'], text_item['y']), str(random_numbers_for_image[j]), font=font, fill="white")
                # Add nameTile text
                font = ImageFont.truetype("UID LETTER.ttf", name_font_size)
                draw.text((name_x, name_y), name, font=font, fill="white")
                temp_img_byte_arr = io.BytesIO()
                temp_image.save(temp_img_byte_arr, format='PNG')
                temp_img_byte_arr = temp_img_byte_arr.getvalue()
                zip_file.writestr(f"edited_image_{name}.png", temp_img_byte_arr)
        
        zip_buffer.seek(0)

        st.download_button(
            label="Download All Images as ZIP",
            data=zip_buffer,
            file_name="edited_images.zip",
            mime="application/zip"
        )
