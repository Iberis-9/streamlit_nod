import streamlit as st

def apod_banner(url: str, height: int = 250):
    st.markdown(
        f"""
        <div style="
            width: 100%;
            max-height: {height}px;
            overflow: hidden;
            border-radius: 10px;
        ">
            <img src="{url}"
                 style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        """,
        unsafe_allow_html=True
    )
