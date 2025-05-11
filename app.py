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

# Custom CSS (unchanged)
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
    
    /* Difficulty badge styles */
    .difficulty-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 10px;
    }
    .low-difficulty {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .medium-difficulty {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .high-difficulty {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    
    /* Difficulty tabs */
    .difficulty-tabs {
        display: flex;
        margin-bottom: 20px;
    }
    
    .difficulty-tab {
        flex: 1;
        text-align: center;
        padding: 10px;
        cursor: pointer;
        border: 1px solid #E5E7EB;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .difficulty-tab:first-child {
        border-radius: 8px 0 0 8px;
    }
    
    .difficulty-tab:last-child {
        border-radius: 0 8px 8px 0;
    }
    
    .difficulty-tab.active-low {
        background-color: #D1FAE5;
        color: #065F46;
        border-color: #A7F3D0;
    }
    
    .difficulty-tab.active-medium {
        background-color: #FEF3C7;
        color: #92400E;
        border-color: #FDE68A;
    }
    
    .difficulty-tab.active-high {
        background-color: #FEE2E2;
        color: #991B1B;
        border-color: #FECACA;
    }
    
    .info-card {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state to store generated clusters across difficulties
if 'generated_clusters' not in st.session_state:
    st.session_state.generated_clusters = {
        'Low': None,
        'Medium': None,
        'High': None
    }
    
if 'last_topic' not in st.session_state:
    st.session_state.last_topic = None
    
if 'all_keywords' not in st.session_state:
    st.session_state.all_keywords = set()

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
    2. Click "Generate Content Clusters"
    3. Switch between difficulty tabs to see different keyword options
    4. Download your results as CSV
    
    #### Difficulty Levels (SEO Standard):
    
    - **Low**: 
      - 1-2 words, more specific phrases
      - 10-300 monthly searches
      - KD score below 30
      - Minimal competition
    
    - **Medium**: 
      - 1-2 words, focused phrases
      - 300-1,000 monthly searches
      - KD score 30-60
      - Moderate competition
    
    - **High**: 
      - 1-2 words, broader terms
      - 1,000+ monthly searches
      - KD score above 60
      - Strong competition, major sites
    
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
    topic = st.text_input("Main Topic of Interest", placeholder="e.g., Organic Gardening")
    submit_button = st.form_submit_button("✨ Generate Content Clusters for All Difficulty Levels")
st.markdown('</div>', unsafe_allow_html=True)

# Function to get difficulty-specific parameters
def get_difficulty_parameters(difficulty):
    if difficulty == "Low":
        return {
            "description": "more specific, niche keywords with minimal competition that are easier to rank for",
            "search_volume": "lower search volume (typically 10-300 monthly searches)",
            "complexity": "1-2 words, specific phrase combinations",
            "examples": "\"organic fertilizers\", \"companion planting\" (1-2 words)",
            "competition": "low competition score (0-30%), few established websites ranking for these terms",
            "kd_score": "KD (Keyword Difficulty) score below 30",
            "serp_features": "fewer SERP features, less established content",
            "intent": "often specific informational or niche transactional intent"
        }
    elif difficulty == "Medium":
        return {
            "description": "moderately competitive terms with decent traffic potential but still attainable",
            "search_volume": "moderate search volume (typically 300-1,000 monthly searches)",
            "complexity": "1-2 words, focused industry-specific phrases",
            "examples": "\"vegetable gardening\", \"soil amendments\" (1-2 words)",
            "competition": "medium competition score (30-60%), some established websites but ranking opportunities exist",
            "kd_score": "KD (Keyword Difficulty) score between 30-60",
            "serp_features": "some SERP features, moderate content quality needed",
            "intent": "mix of informational and commercial intent"
        }
    else:  # High
        return {
            "description": "highly competitive keywords with strong traffic potential but difficult to rank for",
            "search_volume": "high search volume (typically 1,000+ monthly searches)",
            "complexity": "1-2 words, broader industry terms",
            "examples": "\"gardening\", \"plant care\" (1-2 words)",
            "competition": "high competition score (60%+), many established websites with high authority",
            "kd_score": "KD (Keyword Difficulty) score above 60",
            "serp_features": "many SERP features, highly optimized content required",
            "intent": "often commercial or navigational intent with high competition"
        }

# Function to generate content clusters for all difficulty levels
def generate_all_content_clusters(topic):
    all_clusters = {}
    all_keywords_set = set()
    
    for difficulty in ["Low", "Medium", "High"]:
        df = generate_content_clusters(topic, difficulty, all_keywords_set)
        if df is not None:
            all_clusters[difficulty] = df
            # Add these keywords to our overall set to avoid duplication
            all_keywords_set.update(df['keyword'].str.lower().tolist())
    
    return all_clusters, all_keywords_set

# Function to generate content clusters for a specific difficulty
def generate_content_clusters(topic, difficulty, existing_keywords=None):
    if existing_keywords is None:
        existing_keywords = set()
        
    # Set up LangChain with OpenAI
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    
    # Get difficulty-specific parameters
    difficulty_params = get_difficulty_parameters(difficulty)
    
    # Create the system prompt with more specific difficulty differentiation
    system_prompt = f"""
    Role: You are an experienced SEO specialist and content strategist with expertise in keyword difficulty analysis.
    Task: Generate EXACTLY 20 content clusters for the topic "{topic}" with strictly "{difficulty}" difficulty level.

    CRITICAL: 
    - You MUST output EXACTLY 20 keywords, no more and no less.
    - EACH KEYWORD MUST BE EITHER 1 OR 2 WORDS LONG. Both 1-word and 2-word keywords are acceptable.
    - The keywords should include a mix of both 1-word and 2-word combinations.
    - Each keyword MUST be STRICTLY within the "{difficulty}" difficulty category as defined below.
    - Keywords must be distinctive from keywords that would be appropriate for other difficulty levels.

    ---------------------------------------
    DETAILED SEO KEYWORD DIFFICULTY CRITERIA
    ---------------------------------------

    FOR {difficulty.upper()} DIFFICULTY KEYWORDS:
    - Description: {difficulty_params["description"]}
    - Search Volume: {difficulty_params["search_volume"]}
    - Word Count/Format: {difficulty_params["complexity"]} (MUST BE EXACTLY 1-2 WORDS - NO EXCEPTIONS)
    - Competition Level: {difficulty_params["competition"]}
    - Keyword Difficulty Score: {difficulty_params["kd_score"]}
    - SERP Features: {difficulty_params["serp_features"]}
    - User Intent: {difficulty_params["intent"]}
    - Examples: {difficulty_params["examples"]}

    Process:
    1. Generate EXACTLY 20 content cluster keywords for "{topic}" that are STRICTLY {difficulty.upper()} difficulty level.
    2. EVERY keyword MUST be either 1 or 2 words long - this is mandatory.
    3. Double-check each keyword against ALL criteria above to ensure it truly fits the {difficulty} difficulty profile.
    4. Each keyword MUST be related to the main topic "{topic}".
    5. The keywords should be:
       a. Genuinely popular and searched (not fabricated terms)
       b. Directly relevant to "{topic}"
       c. Diverse to cover different aspects of the topic
       d. Suitable for creating multiple content pieces

    FOR THE OUTPUT JSON:
    - Include specific justification for WHY each keyword matches {difficulty.upper()} difficulty criteria
    - Explicitly state the estimated search volume range, competition level, and word count
    - Provide truly distinct article ideas that would work for each keyword
    - The output MUST contain EXACTLY 20 keyword entries, no more and no less

    Format results in this JSON schema:
    {{
        "keywords": [
            {{
                "keyword": "Example {difficulty} Difficulty Keyword",
                "difficulty_level": "{difficulty}",
                "search_volume": "Estimated volume of XXX-XXX searches per month",
                "competition_level": "XX% - {difficulty} competition",
                "explanation": "Detailed explanation of why this is a {difficulty.lower()} difficulty keyword with specific SEO metrics",
                "article_idea_1": "Specific title and brief description of a potential article",
                "article_idea_2": "Specific title and brief description of a potential article"
            }},
            ... (18 more entries for a total of EXACTLY 20)
        ]
    }}

    IMPORTANT FINAL CHECK: 
    1. Count your keywords to confirm you have EXACTLY 20 entries
    2. Verify EVERY keyword is EXACTLY 1-2 words only - COUNT THEM CAREFULLY
    3. Any keyword with 3 or more words MUST be removed and replaced
    4. Review your final list and REMOVE any keywords that could be classified in different difficulty categories
    5. If you had to remove any keywords that didn't meet the criteria, replace them with new valid keywords to maintain EXACTLY 20 total.
    """
    
    # Create the user message with emphasis on avoiding existing keywords
    existing_keywords_list = ", ".join(f'"{k}"' for k in existing_keywords)
    user_prompt = f"""
    Generate EXACTLY 20 content cluster keywords for the topic: {topic}. 
    
    CRITICAL REQUIREMENTS:
    1. ALL keywords MUST contain EXACTLY 1-2 WORDS ONLY - NEVER more than 2 words - NO EXCEPTIONS!
    2. Include a mix of both single-word keywords and two-word keywords.
    3. I need STRICTLY {difficulty.upper()} difficulty level keywords according to standard SEO metrics
    4. These keywords must be distinctly different from what would be found in other difficulty levels
    5. DO NOT USE any of the following keywords that have already been generated: {existing_keywords_list}
    
    For {difficulty.upper()} difficulty keywords:
    - Word count: EXACTLY 1-2 words only - this is absolutely mandatory
    - Search volume: {difficulty_params["search_volume"]}
    - Competition: {difficulty_params["competition"]} 
    - KD score: {difficulty_params["kd_score"]}
    
    Please verify each keyword against these criteria. Include specific SEO metrics for each keyword and explain exactly why it meets {difficulty.upper()} difficulty standards.
    
    REMEMBER: I need EXACTLY 20 keywords, no more, no less, ALL EXACTLY 1-2 WORDS MAX, and COMPLETELY DIFFERENT from already existing keywords.
    """
    
    # Call the LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Parse the JSON response with improved handling
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
    
    # Convert to DataFrame with exact count enforcement
    if 'keywords' in result:
        df = pd.DataFrame(result['keywords'])
        
        # ENSURE EXACTLY 20 KEYWORDS
        if len(df) > 20:
           df = df.iloc[:20]  # Take only the first 20
        elif len(df) < 20:
           # Silently handle the case when fewer than 20 keywords are returned
           pass
        
        # Validate keyword length - ensure only 1-2 words
        valid_keywords = []
        for i, row in df.iterrows():
            keyword = row['keyword'].strip()
            word_count = len(keyword.split())
            if word_count <= 2:
                valid_keywords.append(row)
            else:
                # For keywords with more than 2 words, try to extract a 1-2 word version
                words = keyword.split()
                if len(words) > 2:
                    # Take just the first 2 words
                    keyword_fixed = " ".join(words[:2])
                    row_copy = row.copy()
                    row_copy['keyword'] = keyword_fixed
                    valid_keywords.append(row_copy)
        
        # If we have valid keywords, replace the DataFrame
        if valid_keywords:
            df = pd.DataFrame(valid_keywords)
            # If we have fewer than 20 valid keywords, that's okay
        
        # Add a numbered index starting from 1 instead of 0
        df.index = df.index + 1
        
        # Reset index to create a column with numbering starting from 1
        df = df.reset_index().rename(columns={"index": "number"})
        
        return df
    return None

# Process form submission
if submit_button:
    if not topic:
        st.error("Please enter a main topic of interest.")
    else:
        # Check if we're generating for a new topic
        if st.session_state.last_topic != topic:
            # Reset all stored keywords
            st.session_state.all_keywords = set()
            
            with st.spinner(f"✨ Generating content clusters for all difficulty levels... This may take a minute or two."):
                try:
                    # Generate clusters for all difficulties at once
                    all_clusters, all_keywords = generate_all_content_clusters(topic)
                    
                    # Store the results in session state
                    st.session_state.generated_clusters = all_clusters
                    st.session_state.all_keywords = all_keywords
                    st.session_state.last_topic = topic
                    
                    # Success message
                    st.markdown(f"""
                    <div class="success-message">
                        <h3>✅ Success!</h3>
                        <p>Generated content clusters for <strong>"{topic}"</strong> at all difficulty levels!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add info message about tab navigation
                    st.markdown(f"""
                    <div class="info-card">
                        <h4>👀 View Your Results</h4>
                        <p>Use the difficulty tabs below to see content clusters for each difficulty level.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            # Topic is the same, just show stored results
            st.markdown(f"""
            <div class="success-message">
                <h3>✅ Results for "{topic}"</h3>
                <p>Showing previously generated content clusters across all difficulty levels.</p>
            </div>
            """, unsafe_allow_html=True)

# Display difficulty tabs if we have results
if st.session_state.generated_clusters['Low'] is not None or st.session_state.generated_clusters['Medium'] is not None or st.session_state.generated_clusters['High'] is not None:
    # Create difficulty tabs
    col1, col2, col3 = st.columns(3)
    
    # Create custom tabs with active styling
    difficulty_options = ["Low", "Medium", "High"]
    
    # Initialize current difficulty if not in session state
    if 'current_difficulty' not in st.session_state:
        st.session_state.current_difficulty = "Low"
    
    # Render the tabs with custom HTML
    st.markdown('<div class="difficulty-tabs">', unsafe_allow_html=True)
    for difficulty in difficulty_options:
        if difficulty == "Low":
            active_class = "active-low" if st.session_state.current_difficulty == difficulty else ""
        elif difficulty == "Medium":
            active_class = "active-medium" if st.session_state.current_difficulty == difficulty else ""
        else:  # High
            active_class = "active-high" if st.session_state.current_difficulty == difficulty else ""
            
        if st.button(f"{difficulty} Difficulty", key=f"tab_{difficulty}", use_container_width=True):
            st.session_state.current_difficulty = difficulty
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display the current difficulty's data
    current_difficulty = st.session_state.current_difficulty
    df = st.session_state.generated_clusters[current_difficulty]
    
    if df is not None:
        # Display the results in a nice table
        st.subheader(f"{current_difficulty} Difficulty Content Clusters")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.dataframe(
                df,
                column_config={
                    "number": st.column_config.NumberColumn("No.", width="small"),
                    "keyword": st.column_config.TextColumn("Keyword", width="medium"),
                    "difficulty_level": st.column_config.TextColumn("Difficulty", width="small"),
                    "search_volume": st.column_config.TextColumn("Search Volume", width="medium"),
                    "competition_level": st.column_config.TextColumn("Competition", width="medium"),
                    "explanation": st.column_config.TextColumn("Explanation", width="large"),
                    "article_idea_1": st.column_config.TextColumn("Article Idea 1", width="large"),
                    "article_idea_2": st.column_config.TextColumn("Article Idea 2", width="large")
                },
                use_container_width=True,
                height=400,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button for current difficulty
        csv = df.to_csv(index=False)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.download_button(
                label=f"📥 Download {current_difficulty} Difficulty Clusters as CSV",
                data=csv,
                file_name=f"{st.session_state.last_topic.replace(' ', '_')}_{current_difficulty.lower()}_difficulty_content_clusters.csv",
                mime="text/csv",
                use_container_width=True,
            )

# Footer
st.markdown("<footer>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("© 2025 Content Cluster Generator | Built with Streamlit and LangChain")
st.markdown("</footer>", unsafe_allow_html=True)
