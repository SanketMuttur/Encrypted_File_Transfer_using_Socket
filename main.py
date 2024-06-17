import streamlit as st
from streamlit_option_menu import option_menu

st.markdown("<h1 style='text-align: center;'>Safe File Transferring</h1>", unsafe_allow_html=True)

selected = option_menu(
    menu_title= "HOME",
    menu_icon = "house-fill",
    options = ['Select The Action:', 'SEND', 'RECEIVE'],
    icons = ['share-fill', 'file-earmark-arrow-up-fill', 'file-earmark-arrow-down-fill'],
    orientation = "vertical"
)

if selected == "SEND":
    st.switch_page("pages/sender.py")
if selected == "RECEIVE":
    st.switch_page("pages/receiver.py")