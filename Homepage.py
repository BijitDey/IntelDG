import streamlit as st
from PIL import Image

img = Image.open("src/images/affine.jpg")

page_config = {"page_title":"invoice_tool.io","page_icon":img,"layout":"wide"}

st.set_page_config(**page_config)

## Divide the user interface into two parts: column 1 (small) and column 2 (large).
#"""This code assigns the st.columns([1, 8]) statement to the variables col1 and col2, 
#which divide the user interface into two columns. Column 1 will be smaller in width, 
# while column 2 will be larger.
#"""
## logo
with st.sidebar:
    st.markdown("""<div style='text-align: left; margin-top:-200px;margin-left:-40px;'>
    <img src="https://affine.ai/wp-content/uploads/2023/05/Affine-Logo.svg" alt="logo" width="300" height="60">
    </div>""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; margin-top:-70px; margin-bottom: 5px;margin-left: -50px;'>
    <h2 style='font-size: 60px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
    <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    IntelDG
    </span>
    <span style='font-size: 60%;'>
    <sup style='position: relative; top: 5px; color: #ed4965;'>by Affine</sup>
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Extract the text from uploaded pdf

st.markdown("""
## Welcome to our Document Generator Application!

This application has several tabs, each with its own functionality:

### Document Evolution
This tab allows users to compare different versions of a document side by side. Users can select the versions from a dropdown menu, and the changes are highlighted for easy comparison.

### Text Highlighter & PDF Exporter
This tab enables users to highlight specific text in the original document. The highlighted document can then be exported as a new PDF, making it easy to focus on key information.

### Updated Document Downloader
This tab provides a simple way for users to download the most recent version of the document. It ensures users always have access to the latest information.

### Document Version History
This tab maintains a record of all changes made to the document over time. It stores the history in a dataframe, allowing users to track the evolution of the document from version 1 to the current version.
""")

