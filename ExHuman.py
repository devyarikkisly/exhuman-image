import streamlit as st
import base64
import requests
import logging

def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

log_messages = []

def log_to_interface(message):
    log_messages.append(message)
    if len(log_messages) > 10:
        log_messages.pop(0)


logging.basicConfig(level=logging.INFO)

def send_request(token, image_b64, prompt, style, gender, skin_color, auto_detect_hair_color, nsfw_policy):
    url = "https://api.exh.ai/image/v1/generate_gallery_image"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "identity_image_b64": image_b64,
        "prompt": prompt,
        "style": style,
        "gender": gender,
        "skin_color": skin_color,
        "auto_detect_hair_color": auto_detect_hair_color,
        "nsfw_policy": nsfw_policy
    }

    log_to_interface(f"Sending request to {url}")
    log_to_interface(f"Request data: {data}")
    log_to_interface(f"Request headers: {headers}")

    response = requests.post(url, headers=headers, json=data)

    log_to_interface(f"Response status code: {response.status_code}")
    log_to_interface(f"Response text: {response.text}")

    if response.status_code == 200:
        return response.json().get("image_b64")
    else:
        log_to_interface(f"Error: {response.status_code}")
        return None


st.title("Image Generator")
st.write("Upload an image and configure parameters to generate a new one.")

token = st.text_input("Enter your API token", type="password")

if not token:
    st.warning("Please enter your API token to proceed.")

uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_image and token:
    st.image(uploaded_image, caption="Uploaded Image", width=150)

    image_b64 = encode_image(uploaded_image)

    prompt = st.text_input("Prompt", value="on the beach during sunset")

    style = st.selectbox("Style", ["realistic", "anime"])

    skin_color = st.selectbox("Skin color", ["pale", "white", "tanned", "black"])

    gender = st.text_input("Gender", value="")
    auto_detect_hair_color = st.checkbox("Auto-detect hair color", value=True)
    nsfw_policy = st.selectbox("NSFW Policy", ["filter", "blur", "allow"])

    if st.button("Generate Image"):
        generated_image_b64 = send_request(
            token, image_b64, prompt, style, gender, skin_color, auto_detect_hair_color, nsfw_policy
        )

        if generated_image_b64:
            log_to_interface(f"Generated Image (Base64): {generated_image_b64[:50]}...")

            try:
                image_data = base64.b64decode(generated_image_b64)

                log_to_interface(f"Decoded image size: {len(image_data)} bytes")

                st.image(image_data, caption="Generated Image", use_column_width=True)
            except Exception as e:
                st.error(f"Error decoding image: {str(e)}")
                log_to_interface(f"Error decoding image: {str(e)}")

st.subheader("Logs")
for log in log_messages:
    st.text(log)
