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
    
    #### Difficulty Levels (SEO Standard):
    
    - **Low**: 
      - 4+ words, specific phrases
      - 10-300 monthly searches
      - KD score below 30
      - Minimal competition
    
    - **Medium**: 
      - 3-4 words, focused phrases
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
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input("Main Topic of Interest", placeholder="e.g., Organic Gardening")
    
    with col2:
        difficulty = st.selectbox(
            "Keyword Difficulty",
            ["Low", "Medium", "High"],
            help="Low difficulty keywords are easier to rank for, while high difficulty keywords are more competitive but may have higher search volume."
        )
        
        # Display visual indicator of selected difficulty
        if difficulty == "Low":
            badge_color = "low-difficulty"
        elif difficulty == "Medium":
            badge_color = "medium-difficulty"
        else:
            badge_color = "high-difficulty"
        
        st.markdown(f'<span class="difficulty-badge {badge_color}">{difficulty}</span>', unsafe_allow_html=True)
    
    submit_button = st.form_submit_button("✨ Generate Content Clusters")
st.markdown('</div>', unsafe_allow_html=True)

# Function to get difficulty-specific parameters
def get_difficulty_parameters(difficulty):
    if difficulty == "Low":
        return {
            "description": "long-tail, specific keywords with minimal competition that are much easier to rank for",
            "search_volume": "lower search volume (typically 10-300 monthly searches)",
            "complexity": "highly specific, longer phrases (typically 4+ words)",
            "examples": "very specific how-to guides, niche questions, micro-topics with limited competition",
            "competition": "low competition score (0-30%), few established websites ranking for these terms",
            "kd_score": "KD (Keyword Difficulty) score below 30",
            "serp_features": "fewer SERP features, less established content",
            "intent": "often highly specific informational or long-tail transactional intent"
        }
    elif difficulty == "Medium":
        return {
            "description": "moderately competitive terms with decent traffic potential but still attainable",
            "search_volume": "moderate search volume (typically 300-1,000 monthly searches)",
            "complexity": "more focused mid-tail phrases (usually 3-4 words)",
            "examples": "specific questions, comparison posts, focused topic guides with moderate competition",
            "competition": "medium competition score (30-60%), some established websites but ranking opportunities exist",
            "kd_score": "KD (Keyword Difficulty) score between 30-60",
            "serp_features": "some SERP features, moderate content quality needed",
            "intent": "mix of informational and commercial intent"
        }
    else:  # High
        return {
            "description": "highly competitive keywords with strong traffic potential but difficult to rank for",
            "search_volume": "high search volume (typically 1,000+ monthly searches)",
            "complexity": "shorter, broader terms (often 1-2 words)",
            "examples": "major topic guides, competitive reviews, popular products or services",
            "competition": "high competition score (60%+), many established websites with high authority",
            "kd_score": "KD (Keyword Difficulty) score above 60",
            "serp_features": "many SERP features, highly optimized content required",
            "intent": "often commercial or navigational intent with high competition"
        }

# Function to generate content clusters
def generate_content_clusters(topic, difficulty):
    # Set up LangChain with OpenAI
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    
    # Get difficulty-specific parameters
    difficulty_params = get_difficulty_parameters(difficulty)
    
    # Create the system prompt with more specific difficulty differentiation and emphasis on EXACTLY 20 keywords
    system_prompt = f"""
    Role: You are an experienced SEO specialist and content strategist with expertise in keyword difficulty analysis.
    Task: Generate EXACTLY 20 content clusters for the topic "{topic}" with strictly "{difficulty}" difficulty level and NO overlap with other difficulty levels.

    CRITICAL: 
    - You MUST output EXACTLY 20 keywords, no more and no less.
    - The user has reported issues with keywords not properly matching their stated difficulty levels. You MUST ensure EVERY keyword you generate is STRICTLY within the "{difficulty}" difficulty category as defined below.

    ---------------------------------------
    DETAILED SEO KEYWORD DIFFICULTY CRITERIA
    ---------------------------------------

    FOR {difficulty.upper()} DIFFICULTY KEYWORDS:
    - Description: {difficulty_params["description"]}
    - Search Volume: {difficulty_params["search_volume"]}
    - Word Count/Format: {difficulty_params["complexity"]}
    - Competition Level: {difficulty_params["competition"]}
    - Keyword Difficulty Score: {difficulty_params["kd_score"]}
    - SERP Features: {difficulty_params["serp_features"]}
    - User Intent: {difficulty_params["intent"]}
    - Examples: {difficulty_params["examples"]}

    Process:
    1. Generate EXACTLY 20 content cluster keywords for "{topic}" that are STRICTLY {difficulty.upper()} difficulty level.
    2. Double-check each keyword against ALL criteria above to ensure it truly fits the {difficulty} difficulty profile.
    3. Each keyword MUST include the main topic "{topic}" or a very close variant.
    4. The keywords should be:
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
                "article_idea_2": "Specific title and brief description of another potential article"
            }},
            ... (18 more entries for a total of EXACTLY 20)
        ]
    }}

    IMPORTANT FINAL CHECK: 
    1. Count your keywords to confirm you have EXACTLY 20 entries
    2. Review your final list and REMOVE any keywords that could be classified in different difficulty categories. Every keyword MUST be undeniably a {difficulty.upper()} difficulty keyword.
    3. If you had to remove any keywords that didn't meet the criteria, replace them with new valid keywords to maintain EXACTLY 20 total.
    """
    
    # Create the user message
    user_prompt = f"""
    Generate EXACTLY 20 content cluster keywords for the topic: {topic}. 
    
    I need STRICTLY {difficulty.upper()} difficulty level keywords according to standard SEO metrics. Previous results showed keywords that overlapped between difficulty levels.
    
    For {difficulty.upper()} difficulty keywords:
    - Word count: {difficulty_params["complexity"]}
    - Search volume: {difficulty_params["search_volume"]}
    - Competition: {difficulty_params["competition"]} 
    - KD score: {difficulty_params["kd_score"]}
    
    Please verify each keyword against these criteria. Include specific SEO metrics for each keyword and explain exactly why it meets {difficulty.upper()} difficulty standards.
    
    REMEMBER: I need EXACTLY 20 keywords, no more, no less.
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
        with st.spinner(f"✨ Generating {difficulty.lower()} difficulty content clusters... This may take a minute."):
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
                    
                    # Add a difficulty badge column
                    if 'difficulty_level' not in df.columns:
                        df['difficulty_level'] = difficulty
                    
                    # Display the results in a nice table
                    st.subheader("Your Content Clusters")
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
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.download_button(
                            label="📥 Download Content Clusters as CSV",
                            data=csv,
                            file_name=f"{topic.replace(' ', '_')}_{difficulty.lower()}_difficulty_content_clusters.csv",
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
