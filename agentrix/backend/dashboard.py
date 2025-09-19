import streamlit as st

def main():
    st.title("Welcome to the AgentriX Dashboard")
    st.write("This is the main dashboard for the AgentriX project.")
    
    # Add more components and functionality as needed
    st.sidebar.title("Navigation")
    st.sidebar.write("Select an option from the sidebar to navigate.")

if __name__ == "__main__":
    main()