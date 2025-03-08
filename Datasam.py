import streamlit as st
import chardet
import pandas as pd
from openai import OpenAI
import io
import os

# Model configuration for different AI services
MODEL_CONFIGS = {
    "DeepSeek R1": {
        "base_url": "https://api.perplexity.ai",
        "model": "r1-1776",
        "service": "perplexity"
    },
    "GPT-4": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "service": "openai"
    },
    "GPT-4 Turbo": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4-0125-preview",
        "service": "openai"
    }
}

# Initialize session state for page navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Report Analysis"

# Configure Streamlit page with custom settings
st.set_page_config(
    page_title="Data Report Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ginug/Datasampublic',
        'Report a bug': "https://github.com/ginug/Datasampublic/issues",
        'About': "# Data Report Analyzer\nAn AI-powered tool for analyzing data reports."
    }
)

# Initialize session state for persistent storage
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {
        "openai": "",
        "perplexity": ""
    }

# Custom CSS for consistent styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #0E1117;
    }
    .stTitle {
        color: #1E88E5;
        font-size: 3rem !important;
    }
    .stSubheader {
        color: #0D47A1;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
    .insight-box {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .evidence-box {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #43a047;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .query-box {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #ffd700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .api-key-input {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border: 1px solid #333333;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .stMarkdown {
        color: #FFFFFF;
    }
    .stTextInput>div>div>input {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 5px;
        color: #FFFFFF;
    }
    .stSelectbox>div>div>select {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 5px;
        color: #FFFFFF;
    }
    .stExpander {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stDataFrame {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 5px;
    }
    /* Ensure all text has good contrast */
    .stMarkdown, .stTextInput label, .stSelectbox label, .stExpander label {
        color: #FFFFFF !important;
    }
    /* Style for sidebar headers */
    .css-1d391kg .sidebar-content h1, 
    .css-1d391kg .sidebar-content h2, 
    .css-1d391kg .sidebar-content h3 {
        color: #1E88E5 !important;
    }
    /* Override any light theme styles */
    [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
    }
    [data-testid="stSidebar"] * {
        background-color: #0E1117 !important;
    }
    /* Ensure links are visible */
    a {
        color: #1E88E5 !important;
    }
    a:hover {
        color: #1565C0 !important;
    }
    /* Ensure placeholder text is visible but slightly muted */
    ::placeholder {
        color: #888888 !important;
    }
    /* Page Navigation Styles */
    .page-nav {
        display: flex;
        justify-content: center;
        gap: 1rem;
        padding: 1rem;
        margin-bottom: 2rem;
        background-color: #1E1E1E;
        border-radius: 10px;
        border: 1px solid #333333;
    }
    .page-nav button {
        background-color: transparent;
        color: #FFFFFF;
        border: 1px solid #1E88E5;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .page-nav button.active {
        background-color: #1E88E5;
        color: white;
    }
    .page-nav button:hover {
        background-color: #1565C0;
        border-color: #1565C0;
    }
    /* Sidebar Navigation Styles */
    .sidebar-nav {
        margin-bottom: 2rem;
    }
    .sidebar-nav .stRadio > label {
        color: #1E88E5 !important;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.5rem;
    }
    .sidebar-nav .stRadio > div {
        border-radius: 5px;
        background-color: #1E1E1E !important;
        padding: 0.5rem;
    }
    .sidebar-nav .stRadio > div > label {
        color: #FFFFFF !important;
    }
    .sidebar-nav .stRadio > div > label:hover {
        color: #1E88E5 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("### 📍 Navigation")
pages = ["Report Analysis", "Data Visualization"]
st.session_state.current_page = st.sidebar.radio(
    "",
    pages,
    index=pages.index(st.session_state.current_page),
    key="page_selector",
    label_visibility="collapsed"
)

# Model selection in sidebar
st.sidebar.markdown("---")
st.sidebar.title("Model Settings")
selected_model = st.sidebar.selectbox(
    "Choose AI Model",
    options=list(MODEL_CONFIGS.keys()),
    index=0  # Default to DeepSeek R1
)

# API Key input section in sidebar
st.sidebar.markdown("### 🔑 API Keys")
st.sidebar.markdown("""
    <div class='api-key-input'>
        Please enter your API key for the required model
    </div>
""", unsafe_allow_html=True)

# API Key inputs with secure password fields
openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.api_keys["openai"],
    key="openai_key_input"
)
st.session_state.api_keys["openai"] = openai_key

perplexity_key = st.sidebar.text_input(
    "Perplexity API Key",
    type="password",
    value=st.session_state.api_keys["perplexity"],
    key="perplexity_key_input"
)
st.session_state.api_keys["perplexity"] = perplexity_key

def get_client(model_name):
    """
    Initialize and return the appropriate API client based on the selected model.
    
    Args:
        model_name (str): Name of the selected model
        
    Returns:
        OpenAI: Configured client for the selected service
        
    Raises:
        st.stop(): If API key is missing or client initialization fails
    """
    config = MODEL_CONFIGS[model_name]
    
    if config["service"] == "openai":
        api_key = st.session_state.api_keys["openai"]
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
            st.stop()
        try:
            return OpenAI(
                api_key=api_key,
                base_url="https://api.openai.com/v1"
            )
        except Exception as e:
            st.error(f"⚠️ Error initializing OpenAI client: {str(e)}")
            st.stop()
    else:  # perplexity service
        api_key = st.session_state.api_keys["perplexity"]
        if not api_key:
            st.error("⚠️ Please enter your Perplexity API key in the sidebar.")
            st.stop()
        try:
            # Set environment variable for Perplexity API key
            os.environ["OPENAI_API_KEY"] = api_key
            
            # Create client with all parameters at initialization
            return OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai",
                default_headers={
                    "Authorization": f"Bearer {api_key}"
                }
            )
        except Exception as e:
            st.error(f"⚠️ Error initializing Perplexity client: {str(e)}")
            st.stop()

def get_insights(client, model_name, messages):
    """
    Generate insights using the selected AI model.
    
    Args:
        client (OpenAI): Configured API client
        model_name (str): Name of the selected model
        messages (list): List of message dictionaries for the API call
        
    Returns:
        str: Generated response from the AI model
        
    Raises:
        st.stop(): If API call fails
    """
    with st.spinner('🤔 Analyzing...'):
        config = MODEL_CONFIGS[model_name]
        
        # Set up model-specific parameters
        params = {
            "model": config["model"],
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 4000
        }
        
        # Add model-specific parameters for Perplexity
        if config["service"] == "perplexity":
            params.update({
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            })
        
        try:
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error during API call: {str(e)}")
            st.stop()

def handle_file_upload(file, file_type="csv"):
    """
    Handle file upload and return processed data.
    
    Args:
        file: Uploaded file object
        file_type (str): Type of file ("csv" or "txt")
        
    Returns:
        Union[pd.DataFrame, str]: Processed data as DataFrame for CSV or string for text
    """
    try:
        if file is None:
            return None
        
        bytes_data = file.read()
        encoding = chardet.detect(bytes_data)['encoding']
        
        if file_type == "csv":
            try:
                return pd.read_csv(io.StringIO(bytes_data.decode(encoding)))
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                return None
        else:  # txt
            try:
                return bytes_data.decode(encoding)
            except Exception as e:
                st.error(f"Error reading text file: {str(e)}")
                return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Display current page content
if st.session_state.current_page == "Report Analysis":
    # Application header with description
    st.title("Report Analyzer")
    st.markdown("""
        <div style='background-color: #1E1E1E; padding: 1rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid #333333; color: #FFFFFF;'>
            Upload your data files to get AI-powered insights and analysis. This tool helps you:
            * 📈 Analyze CSV data files
            * 📝 Process text appendices
            * 🤖 Generate AI insights
            * 🔍 Ask custom questions
        </div>
    """, unsafe_allow_html=True)

    # File upload section with two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📁 Upload Summary CSV")
        summary_file = st.file_uploader("Choose a CSV file", type="csv")

    with col2:
        st.markdown("### 📄 Upload Appendix Text")
        appendix_file = st.file_uploader("Choose a text file", type="txt")

    # Load and display uploaded data
    if summary_file is not None:
        with st.expander("📊 Summary Report", expanded=True):
            with st.spinner("Loading CSV file..."):
                summary_data = handle_file_upload(summary_file, "csv")
                if summary_data is not None:
                    st.dataframe(summary_data, use_container_width=True)

    if appendix_file is not None:
        with st.expander("📑 Appendix Content", expanded=True):
            with st.spinner("Loading text file..."):
                appendix_text = handle_file_upload(appendix_file, "txt")
                if appendix_text is not None:
                    st.text_area("Appendix Content", appendix_text, height=200)

    # Analysis section
    if summary_file and appendix_file:
        st.markdown("---")
        
        # Run Analysis button
        run_analysis = st.button("🚀 Run Analysis", type="primary")
        
        if run_analysis:
            client = get_client(selected_model)
            summary_content = summary_file.getvalue().decode("utf-8")
            appendix_content = appendix_file.getvalue().decode("utf-8")

            # Generate main insights
            st.markdown("### 🎯 Key Insights")
            insights_messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in data analysis."},
                {"role": "user", "content": f"Summary file: {summary_content}\nAppendix: {appendix_content}\nProvide a brief summary of insights from the data."}
            ]
            insights = get_insights(client, selected_model, insights_messages)
            st.markdown(f'<div class="insight-box">{insights}</div>', unsafe_allow_html=True)

            # Generate supporting evidence
            st.markdown("### 📊 Supporting Evidence")
            evidence_messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in data analysis."},
                {"role": "user", "content": f"Summary file: {summary_content}\nAppendix: {appendix_content}\nProvide records related to the insights."}
            ]
            evidence_response = get_insights(client, selected_model, evidence_messages)
            st.markdown(f'<div class="evidence-box">{evidence_response}</div>', unsafe_allow_html=True)

        # Custom Query section with history
        st.markdown("### 🔍 Custom Query")
        query_container = st.container()
        
        with query_container:
            with st.form(key="query_form", clear_on_submit=False):
                user_query = st.text_input(
                    "Ask a specific question about the data:",
                    placeholder="E.g., What are the main trends in the data?",
                    key="query_input"
                )
                col1, col2 = st.columns([3, 1])
                with col1:
                    submit_query = st.form_submit_button("🔍 Submit Query", type="primary", use_container_width=True)
                with col2:
                    clear_history = st.form_submit_button("🗑️ Clear History", type="secondary", use_container_width=True)
            
            if clear_history:
                st.session_state.query_history = []
                st.experimental_rerun()

            if submit_query and user_query:
                try:
                    with st.spinner("Processing query..."):
                        client = get_client(selected_model)
                        summary_content = summary_file.getvalue().decode("utf-8")
                        appendix_content = appendix_file.getvalue().decode("utf-8")
                        
                        query_messages = [
                            {"role": "system", "content": "You are a helpful assistant specialized in data analysis."},
                            {"role": "user", "content": f"Summary file: {summary_content}\nAppendix: {appendix_content}\nQuery: {user_query}"}
                        ]
                        query_response = get_insights(client, selected_model, query_messages)
                        
                        # Add to history
                        st.session_state.query_history.append({
                            "query": user_query,
                            "response": query_response,
                            "model": selected_model
                        })
                        
                        # Display response
                        st.markdown(f'<div class="query-box">{query_response}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
            elif submit_query and not user_query:
                st.warning("Please enter a query before submitting.")

            # Display query history
            if st.session_state.query_history:
                st.markdown("### 📜 Query History")
                for i, item in enumerate(reversed(st.session_state.query_history)):
                    with st.expander(f"Q: {item['query']} (using {item['model']})"):
                        st.markdown(f'<div class="query-box">{item["response"]}</div>', unsafe_allow_html=True)

    else:
        st.info("👆 Please upload both the Summary CSV and Appendix Text files to generate insights.")

    # Footer with version info
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Version 1.0.0</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "Data Visualization":
    st.title("Data Visualization")
    st.markdown("""
        <div style='background-color: #1E1E1E; padding: 1rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid #333333; color: #FFFFFF;'>
            Visualize your data with interactive charts and graphs. Features include:
            * 📊 Interactive charts
            * 📈 Trend analysis
            * 🔍 Data filtering
            * 📉 Custom visualizations
        </div>
    """, unsafe_allow_html=True)
    
    # Add visualization content here
    st.info("🚧 Data visualization features are coming soon! Stay tuned for updates.")


