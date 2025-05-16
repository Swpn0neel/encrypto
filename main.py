import streamlit as st
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Image Steganography", layout="centered")

def text_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(char, 2)) for char in chars if int(char, 2) != 0])

def encode_image(img, message):
    binary_message = text_to_bin(message) + '1111111111111110' 
    img = img.convert('RGB')
    data = np.array(img).copy().astype(np.uint8)
    flat_data = data.flatten()

    if len(binary_message) > len(flat_data):
        raise ValueError("Message too long to encode in this image.")

    for i in range(len(binary_message)):
        byte = flat_data[i]
        bit = int(binary_message[i])
        flat_data[i] = (byte & 0b11111110) | bit

    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data, 'RGB')
    return encoded_img

def decode_image(img):
    img = img.convert('RGB')
    data = np.array(img).astype(np.uint8)
    flat_data = data.flatten()

    bits = [str(byte & 1) for byte in flat_data]
    binary_message = ''.join(bits)

    eof_index = binary_message.find('1111111111111110')
    if eof_index == -1:
        return "[No hidden message found]"

    return bin_to_text(binary_message[:eof_index])

st.title("Encrypto 🕵️‍♂️")
st.subheader('A stenoqraphy tool created by [Swapnoneel](https://x.com/swapnoneel123)')
mode = st.radio("Choose Mode", ["Encrypt", "Decrypt"], horizontal=True)

if mode == "Encrypt":
    st.header("🔐 Encrypt Text into Image")

    with st.form("encryption_form"):
        uploaded_image = st.file_uploader("Upload an Image (PNG or JPG)", type=["png", "jpg", "jpeg"], key="encrypt_image")
        secret_text = st.text_area("Enter Text to Encrypt", key="encrypt_text")
        submit_encrypt = st.form_submit_button("Encrypt and Download")

    if submit_encrypt:
        if uploaded_image and secret_text.strip():
            try:
                image = Image.open(uploaded_image).convert("RGB")
                encoded_img = encode_image(image, secret_text)
                buffer = io.BytesIO()
                encoded_img.save(buffer, format="PNG")
                byte_img = buffer.getvalue()

                st.success("✅ Encryption Successful!")
                st.download_button(label="📥 Download Encrypted Image", data=byte_img,
                                   file_name="encrypted_image.png", mime="image/png")
                st.image(encoded_img, caption="Encrypted Image Preview", use_column_width=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload an image and enter some text before submitting.")

elif mode == "Decrypt":
    st.header("🔓 Decrypt Text from Image")

    with st.form("decryption_form"):
        uploaded_image = st.file_uploader("Upload an Encrypted Image", type=["png", "jpg", "jpeg"], key="decrypt_image")
        submit_decrypt = st.form_submit_button("Decrypt")

    if submit_decrypt:
        if uploaded_image:
            try:
                image = Image.open(uploaded_image).convert("RGB")
                hidden_message = decode_image(image)
                st.success("✅ Decryption Successful!")
                st.text_area("Hidden Message", hidden_message, height=150)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload an image to decrypt.")
