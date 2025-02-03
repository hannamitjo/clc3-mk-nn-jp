import streamlit as st
from utils import list_objects, upload_object, download_object, delete_object

# Wrapper for caching
@st.cache_data
def download_file(filename):
    return download_object(filename)

def main():
    st.write("## File storage_v4")

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    file = st.file_uploader("Upload your file here", key=st.session_state["uploader_key"])
    if st.button("Upload", disabled=file is None):
        upload_object(file)
        st.session_state["uploader_key"] += 1
        st.rerun()
    
    filenames = list_objects()
    if len(filenames) > 0:
        with st.container(border=True):
            st.write("### Uploaded files:")
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            for i, filename in enumerate(filenames):
                col1.write(filename)
                col2.download_button("",
                                     icon=":material/download:",
                                     data=download_file(filename),
                                     file_name=filename,
                                     key=f"download_button_{i}")
                col3.button("",
                            icon=":material/delete:",
                            on_click=delete_object,
                            kwargs={"filename": filename},
                            key=f"delete_button_{i}")
                
    info_text = '''This application can help with file organization. Files can easily be uploaded into a MINIO file storage. 
    Once the files are needed, a download of the stored files can be triggerd via this web interface.'''

    st.markdown(info_text)


if __name__ == "__main__":
    main()
