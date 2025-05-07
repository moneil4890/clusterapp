import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import os

# Set the API key directly in the code
API_KEY = st.secrets["key"]
os.environ["OPENAI_API_KEY"] = API_KEY

# Set page configuration
st.set_page_config(
    page_title="Content Cluster Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more beautiful and aesthetic look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        padding-top: 1rem;
        background-color: #F9FAFB;
    }
    
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    h1 {
        color: #4F46E5;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    h2, h3 {
        color: #4338CA;
        font-weight: 600;
    }
    
    .stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #4338CA;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    .css-1v3fvcr {
        background-color: #F9FAFB;
    }
    
    .table-container {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .download-btn {
        background-color: #10B981;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .download-btn:hover {
        background-color: #059669;
    }
    
    .sidebar .css-1d391kg {
        background-color: #F3F4F6;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .hero-section h1 {
        color: white;
        margin-bottom: 1rem;
    }
    
    .hero-section p {
        opacity: 0.9;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
    
    .form-container {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .success-message {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }
    
    .stDataFrame {
        border: none !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border: none !important;
    }
    
    footer {
        text-align: center;
        padding: 1.5rem 0;
        color: #6B7280;
    }
    
    /* Custom divider */
    .custom-divider {
        height: 4px;
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        border-radius: 2px;
        margin: 0.5rem 0 1.5rem 0;
        width: 100px;
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.title("Content Cluster Generator")
st.markdown("""
This intelligent app identifies relevant content clusters for your topic of interest.
Build a comprehensive SEO strategy that demonstrates expertise to search engines and engages your audience.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/content.png", width=80)
    st.header("About This Tool")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    #### What are Content Clusters?
    
    Content clusters are groups of related content pieces that establish you as an authority on a specific topic in the eyes of search engines.
    
    #### How to use this app:
    
    1. Enter your main topic of interest
    2. Select the keyword difficulty level
    3. Click "Generate Content Clusters"
    4. Download your results as CSV
    
    #### Benefits:
    
    - Improve search engine rankings
    - Build topical authority
    - Create strategic content plans
    - Save time on keyword research
    """)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Made with:")
    st.markdown("- 💻 Streamlit\n- 🤖 LangChain\n- 🧠 OpenAI GPT-3.5")

# Main form in a container
st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.subheader("Generate Your Content Clusters")
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

with st.form("cluster_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input("Main Topic of Interest", placeholder="e.g., Organic Gardening")
    
    with col2:
        difficulty = st.selectbox(
            "Keyword Difficulty",
            ["Low", "Medium", "High"],
            help="Low difficulty keywords are easier to rank for, while high difficulty keywords are more competitive but may have higher search volume."
        )
    
    submit_button = st.form_submit_button("✨ Generate Content Clusters")
st.markdown('</div>', unsafe_allow_html=True)

# Function to generate content clusters
def generate_content_clusters(topic, difficulty):
    # Set up LangChain with OpenAI
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    
    # Create the system prompt
    system_prompt = """
    Role: You are an experienced SEO specialist and content strategist.
    Task: Your task is to help identify popular and relevant content clusters within a specific topic area. You'll generate a list of high-value keywords that can be used to create multiple articles, focusing on terms with good search volume and relevance to the target audience.
    Context: Users are looking to create comprehensive content strategies around a single topic. They need guidance in identifying related subtopics and keywords that will allow them to create a network of interconnected, valuable content.
    
    Process:
    1. The user has provided their main topic of interest.
    2. Generate 20 related keywords or phrases that represent potential content clusters within that topic. They should be {difficulty} level of difficulty to rank for. The keywords should also:
       a. Include the main topic keywords in almost 100% of cases
       b. Be popular and frequently searched
       c. Be relevant to the main topic
       d. Be diverse enough to cover different aspects or subtopics
       e. Be suitable for creating multiple pieces of content
    3. Present the results in a structured JSON format with the following schema:
    {{
        "keywords": [
            {{
                "keyword": "Example Keyword",
                "explanation": "Why this keyword is important",
                "article_idea_1": "Title and brief description of a potential article",
                "article_idea_2": "Title and brief description of another potential article"
            }},
            ...
        ]
    }}
    
    Tips:
    - Focus on keywords that have good search volume but aren't too broad or competitive.
    - Consider different user intents and stages of the user journey when selecting keywords.
    - Avoid overly niche or obscure terms that might not have broad appeal.
    - Think about how the keywords can be interlinked to create a comprehensive content structure.
    """
    
    system_prompt = system_prompt.replace("{difficulty}", difficulty.lower())
    
    # Create the user message
    user_prompt = f"Please generate 20 content cluster keywords for the topic: {topic}. I need keywords with {difficulty.lower()} difficulty level."
    
    # Call the LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Parse the JSON response
    try:
        # Look for JSON content within the response
        response_text = response.content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
        else:
            # Fallback if no JSON found
            st.error("The API response didn't contain properly formatted JSON data.")
            return None
    except json.JSONDecodeError:
        st.error("Could not parse the API response as JSON.")
        return None
    
    # Convert to DataFrame
    if 'keywords' in result:
        df = pd.DataFrame(result['keywords'])
        return df
    return None

# Process form submission
if submit_button:
    if not topic:
        st.error("Please enter a main topic of interest.")
    else:
        with st.spinner("✨ Generating content clusters... This may take a minute."):
            try:
                df = generate_content_clusters(topic, difficulty)
                if df is not None:
                    # Success message
                    st.markdown(f"""
                    <div class="success-message">
                        <h3>✅ Success!</h3>
                        <p>Generated {len(df)} content clusters for <strong>"{topic}"</strong> with <strong>{difficulty}</strong> difficulty!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display the results in a nice table
                    st.subheader("Your Content Clusters")
                    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<div class="table-container">', unsafe_allow_html=True)
                        st.dataframe(
                            df,
                            column_config={
                                "keyword": st.column_config.TextColumn("Keyword", width="medium"),
                                "explanation": st.column_config.TextColumn("Explanation", width="large"),
                                "article_idea_1": st.column_config.TextColumn("Article Idea 1", width="large"),
                                "article_idea_2": st.column_config.TextColumn("Article Idea 2", width="large")
                            },
                            use_container_width=True,
                            height=400
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.download_button(
                            label="📥 Download Content Clusters as CSV",
                            data=csv,
                            file_name=f"{topic.replace(' ', '_')}_content_clusters.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("<footer>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("© 2025 Content Cluster Generator | Built with Streamlit and LangChain")
st.markdown("</footer>", unsafe_allow_html=True)