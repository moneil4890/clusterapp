import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import os
import time
import re

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

# Custom CSS remains the same
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
    
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    
    .retry-card {
        background-color: #FEF2F2;
        border-left: 5px solid #DC2626;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    
    .progress-section {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .keyword-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
        background-color: #F3F4F6;
        padding: 0.75rem;
        border-radius: 6px;
    }
    
    .keyword-stat {
        text-align: center;
    }
    
    .keyword-count {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .keyword-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'generated_clusters' not in st.session_state:
    st.session_state.generated_clusters = {
        'Low': None,
        'Medium': None,
        'High': None
    }
    
if 'last_topic' not in st.session_state:
    st.session_state.last_topic = None
    
if 'all_keywords' not in st.session_state:
    st.session_state.all_keywords = {
        'Low': set(),
        'Medium': set(),
        'High': set()
    }
    
if 'generation_progress' not in st.session_state:
    st.session_state.generation_progress = {
        'status': 'idle',  # idle, generating, completed, error
        'current_difficulty': None,
        'attempt_count': {
            'Low': 0,
            'Medium': 0,
            'High': 0
        },
        'message': ''
    }
    
if 'generation_error' not in st.session_state:
    st.session_state.generation_error = None

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
    
    col1, col2 = st.columns([3, 1])
    with col1:
        max_retries = st.slider("Maximum generation attempts per difficulty level", 1, 5, 3, 
                              help="Higher values will ensure more distinct keywords across difficulty levels but may take longer")
    
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

# Function to clean and standardize keywords
def clean_keyword(keyword):
    if not keyword:
        return ""
    # Remove any special characters, extra spaces and convert to lowercase
    cleaned = re.sub(r'[^\w\s]', '', keyword.lower().strip())
    return cleaned

# Function to check if keyword already exists in any difficulty level
def keyword_exists(keyword, existing_keywords):
    cleaned_keyword = clean_keyword(keyword)
    
    # Check for exact matches first
    if cleaned_keyword in existing_keywords:
        return True
    
    # Check for similar keywords (if the cleaned keyword is a substring of an existing keyword or vice versa)
    for existing in existing_keywords:
        if cleaned_keyword in existing or existing in cleaned_keyword:
            # If they're very close in length, consider them duplicates
            if abs(len(cleaned_keyword) - len(existing)) <= 3:
                return True
    
    return False

# Function to generate content clusters for a specific difficulty with validation
def generate_content_clusters(topic, difficulty, existing_keywords_list=None, attempt=1):
    if existing_keywords_list is None:
        existing_keywords_list = []
    
    # Set up LangChain with OpenAI
    try:
        llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    except Exception as e:
        st.error(f"Failed to initialize OpenAI: {str(e)}")
        return None
        
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

    FORMAT THE OUTPUT STRICTLY AS ONE JSON OBJECT WITH THIS SCHEMA:
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
            ... (repeat until you have EXACTLY 20 entries, no more, no less)
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
    existing_keywords_txt = ", ".join(f'"{k}"' for k in existing_keywords_list)
    user_prompt = f"""
    Generate EXACTLY 20 content cluster keywords for the topic: "{topic}". 
    
    CRITICAL REQUIREMENTS:
    1. ALL keywords MUST contain EXACTLY 1-2 WORDS ONLY - NEVER more than 2 words - NO EXCEPTIONS!
    2. Include a mix of both single-word keywords and two-word keywords.
    3. I need STRICTLY {difficulty.upper()} difficulty level keywords according to standard SEO metrics.
    4. These keywords must be distinctly different from what would be found in other difficulty levels.
    5. DO NOT USE any of the following keywords that have already been generated: {existing_keywords_txt}
    
    For {difficulty.upper()} difficulty keywords:
    - Word count: EXACTLY 1-2 words only - this is absolutely mandatory
    - Search volume: {difficulty_params["search_volume"]}
    - Competition: {difficulty_params["competition"]} 
    - KD score: {difficulty_params["kd_score"]}
    
    Please verify each keyword against these criteria. Include specific SEO metrics for each keyword and explain exactly why it meets {difficulty.upper()} difficulty standards.
    
    REMEMBER: 
    - I need EXACTLY 20 keywords.
    - NO MORE than 20, NO LESS than 20.
    - ALL must be EXACTLY 1-2 WORDS MAX.
    - COMPLETELY DIFFERENT from already existing keywords.
    
    THIS IS ATTEMPT #{attempt}, please provide the most accurate and distinct keywords possible.
    """
    
    # Call the LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        # Set a timeout to prevent getting stuck
        response = llm.invoke(messages)
        response_text = response.content
    except Exception as e:
        st.error(f"API call failed: {str(e)}")
        return None
    
    # Parse the JSON response with improved handling
    try:
        # Look for JSON content within the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            # Add debug message
            st.session_state.generation_progress['message'] = f"Parsing JSON response for {difficulty} difficulty..."
            result = json.loads(json_str)
        else:
            # Fallback if no JSON found
            st.error(f"The API response for {difficulty} difficulty didn't contain properly formatted JSON data.")
            st.session_state.generation_error = f"Failed to find JSON data in the response for {difficulty} difficulty."
            return None
    except json.JSONDecodeError as e:
        st.error(f"Could not parse the API response as JSON: {str(e)}")
        st.session_state.generation_error = f"JSON parsing error: {str(e)}"
        return None
    
    # Convert to DataFrame with exact count enforcement
    if 'keywords' in result:
        try:
            df = pd.DataFrame(result['keywords'])
            
            # Filter to ensure we have exactly 1-2 word keywords
            valid_keywords = []
            for _, row in df.iterrows():
                keyword = row['keyword'].strip()
                word_count = len(keyword.split())
                
                if word_count <= 2:
                    valid_keywords.append(row)
            
            # If we don't have enough valid keywords, this attempt failed
            if len(valid_keywords) < 20:
                st.session_state.generation_error = f"Only generated {len(valid_keywords)} valid keywords for {difficulty} difficulty. Need exactly 20."
                return None
            
            # Take exactly 20 valid keywords
            valid_df = pd.DataFrame(valid_keywords[:20])
            
            # Add a numbered index starting from 1
            valid_df = valid_df.reset_index().rename(columns={"index": "number"})
            valid_df['number'] = valid_df['number'] + 1  # Start numbering from 1 instead of 0
            
            return valid_df
        except Exception as e:
            st.error(f"Error processing DataFrame: {str(e)}")
            st.session_state.generation_error = f"DataFrame processing error: {str(e)}"
            return None
    else:
        st.error(f"Missing 'keywords' in the API response for {difficulty} difficulty.")
        st.session_state.generation_error = "The API response is missing the 'keywords' field."
        return None

# Function to check if keywords across different difficulty levels are distinct
def check_keyword_distinctness(clusters):
    all_keywords = {
        'Low': set(),
        'Medium': set(),
        'High': set()
    }
    
    # Extract keywords from each difficulty level
    for difficulty, df in clusters.items():
        if df is not None:
            for keyword in df['keyword'].tolist():
                all_keywords[difficulty].add(clean_keyword(keyword))
    
    # Check for overlaps between difficulty levels
    overlaps = {
        'Low_Medium': len(all_keywords['Low'].intersection(all_keywords['Medium'])),
        'Low_High': len(all_keywords['Low'].intersection(all_keywords['High'])),
        'Medium_High': len(all_keywords['Medium'].intersection(all_keywords['High']))
    }
    
    # Return the overlap counts and all keywords
    return overlaps, all_keywords

# Function to generate all content clusters with distinct keywords across difficulties
def generate_all_content_clusters(topic, max_retries=3):
    # Initialize state
    st.session_state.generation_progress['status'] = 'generating'
    st.session_state.generation_progress['message'] = f"Starting content cluster generation for '{topic}'..."
    st.session_state.generation_error = None
    
    # Track existing keywords across all difficulty levels
    all_clusters = {}
    all_keyword_sets = {
        'Low': set(),
        'Medium': set(), 
        'High': set()
    }
    
    difficulties = ["Low", "Medium", "High"]
    
    # First pass: Generate initial clusters for each difficulty
    for difficulty in difficulties:
        st.session_state.generation_progress['current_difficulty'] = difficulty
        st.session_state.generation_progress['message'] = f"Generating {difficulty} difficulty keywords (attempt 1)..."
        st.session_state.generation_progress['attempt_count'][difficulty] += 1
        
        # Generate initial clusters for this difficulty
        try:
            # Get all existing keywords from other difficulties
            existing_keywords = set()
            for d in difficulties:
                if d != difficulty:
                    existing_keywords.update(all_keyword_sets[d])
            
            df = generate_content_clusters(
                topic, 
                difficulty, 
                list(existing_keywords),
                attempt=st.session_state.generation_progress['attempt_count'][difficulty]
            )
            
            if df is not None and len(df) == 20:
                all_clusters[difficulty] = df
                # Extract keywords and add to the set
                keywords = [clean_keyword(k) for k in df['keyword'].tolist()]
                all_keyword_sets[difficulty].update(keywords)
            else:
                st.session_state.generation_error = f"Failed to generate valid {difficulty} difficulty keywords. Please try again."
                st.session_state.generation_progress['status'] = 'error'
                return None
                
        except Exception as e:
            st.session_state.generation_error = f"Error generating {difficulty} difficulty keywords: {str(e)}"
            st.session_state.generation_progress['status'] = 'error'
            return None
    
    # Check for overlaps between difficulty levels
    overlaps, _ = check_keyword_distinctness(all_clusters)
    total_overlaps = sum(overlaps.values())
    
    # Iteratively regenerate to reduce overlaps
    attempt = 2
    while total_overlaps > 0 and attempt <= max_retries:
        # Find the difficulty with the most overlaps
        difficulty_overlaps = {
            'Low': overlaps['Low_Medium'] + overlaps['Low_High'],
            'Medium': overlaps['Low_Medium'] + overlaps['Medium_High'],
            'High': overlaps['Low_High'] + overlaps['Medium_High']
        }
        
        difficulty_to_regenerate = max(difficulty_overlaps, key=difficulty_overlaps.get)
        
        st.session_state.generation_progress['current_difficulty'] = difficulty_to_regenerate
        st.session_state.generation_progress['message'] = f"Regenerating {difficulty_to_regenerate} difficulty keywords (attempt {attempt}) to reduce {difficulty_overlaps[difficulty_to_regenerate]} overlaps..."
        st.session_state.generation_progress['attempt_count'][difficulty_to_regenerate] += 1
        
        # Get all existing keywords from other difficulties
        existing_keywords = set()
        for d in difficulties:
            if d != difficulty_to_regenerate:
                existing_keywords.update(all_keyword_sets[d])
        
        # Regenerate the most problematic difficulty level
        try:
            df = generate_content_clusters(
                topic, 
                difficulty_to_regenerate, 
                list(existing_keywords),
                attempt=st.session_state.generation_progress['attempt_count'][difficulty_to_regenerate]
            )
            
            if df is not None and len(df) == 20:
                # Update with new keywords
                all_clusters[difficulty_to_regenerate] = df
                all_keyword_sets[difficulty_to_regenerate] = {clean_keyword(k) for k in df['keyword'].tolist()}
                
                # Recalculate overlaps
                overlaps, _ = check_keyword_distinctness(all_clusters)
                total_overlaps = sum(overlaps.values())
                
                st.session_state.generation_progress['message'] = f"Reduced overlaps to {total_overlaps} after attempt {attempt}..."
            else:
                # If we couldn't generate valid keywords, keep the existing ones
                st.session_state.generation_progress['message'] = f"Couldn't generate better keywords, keeping the best set found so far..."
                break
                
        except Exception as e:
            # If an error occurs, keep the existing keywords
            st.session_state.generation_error = f"Error during regeneration attempt: {str(e)}"
            break
            
        attempt += 1
        
    # Final check to ensure we have exactly 20 keywords per difficulty
    for difficulty, df in all_clusters.items():
        if len(df) > 20:
            all_clusters[difficulty] = df.iloc[:20].copy()  # Keep only the first 20
            # Reset the numbering
            all_clusters[difficulty] = all_clusters[difficulty].reset_index(drop=True)
            all_clusters[difficulty]['number'] = all_clusters[difficulty].index + 1
        elif len(df) < 20:
            # This should not happen with our controls, but just in case
            st.session_state.generation_error = f"Warning: Generated only {len(df)} keywords for {difficulty} difficulty. Please try again."
            # Update the session state and mark generation complete
    st.session_state.generation_progress['status'] = 'completed'
    st.session_state.generation_progress['message'] = f"Successfully generated distinct content clusters for '{topic}'!"
    st.session_state.all_keywords = all_keyword_sets
    
    return all_clusters

# Processing the form submission
if submit_button and topic:
    # Reset previous results if we're generating for a new topic
    if st.session_state.last_topic != topic:
        st.session_state.generated_clusters = {
            'Low': None,
            'Medium': None,
            'High': None
        }
        st.session_state.all_keywords = {
            'Low': set(),
            'Medium': set(),
            'High': set()
        }
        st.session_state.generation_progress = {
            'status': 'idle',
            'current_difficulty': None,
            'attempt_count': {
                'Low': 0,
                'Medium': 0,
                'High': 0
            },
            'message': ''
        }
        st.session_state.last_topic = topic
    
    # Generate the clusters
    with st.spinner(f"Generating content clusters for '{topic}'..."):
        clusters = generate_all_content_clusters(topic, max_retries)
        
        if clusters:
            st.session_state.generated_clusters = clusters
            # Show success message
            st.markdown('<div class="success-message">', unsafe_allow_html=True)
            st.success(f"✅ Content clusters successfully generated for '{topic}'!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Error message already displayed in the function
            pass

# Display generation progress if we're in the process
if st.session_state.generation_progress['status'] == 'generating':
    st.markdown('<div class="progress-section">', unsafe_allow_html=True)
    
    st.subheader("Generation Progress")
    
    # Show current operation
    if st.session_state.generation_progress['current_difficulty']:
        current_diff = st.session_state.generation_progress['current_difficulty']
        st.markdown(f"🔄 Currently working on: **{current_diff} Difficulty Keywords** (Attempt {st.session_state.generation_progress['attempt_count'][current_diff]})")
    
    # Show message
    if st.session_state.generation_progress['message']:
        st.info(st.session_state.generation_progress['message'])
    
    # Add a progress bar
    difficulties = ["Low", "Medium", "High"]
    completed_difficulties = sum(1 for d in difficulties if st.session_state.generated_clusters[d] is not None)
    progress = completed_difficulties / 3
    
    st.progress(progress)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display error if any
if st.session_state.generation_error:
    st.markdown('<div class="retry-card">', unsafe_allow_html=True)
    st.error(st.session_state.generation_error)
    st.button("Retry Generation", key="retry_button")
    st.markdown('</div>', unsafe_allow_html=True)

# Display results (only if we have results to show)
if any(st.session_state.generated_clusters.values()):
    # Create tabs for the different difficulty levels
    st.markdown('<div class="difficulty-tabs">', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Low Difficulty", "Medium Difficulty", "High Difficulty"])
    
    # Statistics on keywords
    st.markdown('<div class="keyword-stats">', unsafe_allow_html=True)
    
    low_count = len(st.session_state.all_keywords['Low'])
    medium_count = len(st.session_state.all_keywords['Medium'])
    high_count = len(st.session_state.all_keywords['High'])
    total_count = low_count + medium_count + high_count
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="keyword-stat">', unsafe_allow_html=True)
        st.markdown(f'<div class="keyword-count">{total_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-label">Total Keywords</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="keyword-stat">', unsafe_allow_html=True)
        st.markdown(f'<div class="keyword-count">{low_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-label">Low Difficulty</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="keyword-stat">', unsafe_allow_html=True)
        st.markdown(f'<div class="keyword-count">{medium_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-label">Medium Difficulty</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="keyword-stat">', unsafe_allow_html=True)
        st.markdown(f'<div class="keyword-count">{high_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-label">High Difficulty</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display the difficulties in tabs
    with tab1:
        if st.session_state.generated_clusters['Low'] is not None:
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.subheader(f"Low Difficulty Keywords <span class='difficulty-badge low-difficulty'>Easier to Rank</span>", unsafe_allow_html=True)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
            Low difficulty keywords are more specific, niche terms with minimal competition that are easier to rank for. 
            They typically have lower search volume but higher conversion potential due to their specificity.
            """)
            
            # Display the DataFrame with enhanced styling
            st.dataframe(
                st.session_state.generated_clusters['Low'][['number', 'keyword', 'difficulty_level', 'search_volume', 'competition_level', 'explanation', 'article_idea_1', 'article_idea_2']],
                column_config={
                    "number": "No.",
                    "keyword": "Keyword",
                    "difficulty_level": "Difficulty",
                    "search_volume": "Est. Search Volume",
                    "competition_level": "Competition",
                    "explanation": "SEO Explanation",
                    "article_idea_1": "Content Idea 1",
                    "article_idea_2": "Content Idea 2"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Add download button
            low_csv = st.session_state.generated_clusters['Low'].to_csv(index=False)
            st.download_button(
                label="📥 Download Low Difficulty Keywords",
                data=low_csv,
                file_name=f"{topic.replace(' ', '_')}_low_difficulty_keywords.csv",
                mime="text/csv",
                key="download_low",
                use_container_width=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    with tab2:
        if st.session_state.generated_clusters['Medium'] is not None:
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.subheader(f"Medium Difficulty Keywords <span class='difficulty-badge medium-difficulty'>Moderate Competition</span>", unsafe_allow_html=True)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
            Medium difficulty keywords are moderately competitive terms with decent traffic potential but still attainable ranking positions. 
            They offer a balance between search volume and competition level, ideal for established sites seeking growth.
            """)
            
            # Display the DataFrame with enhanced styling
            st.dataframe(
                st.session_state.generated_clusters['Medium'][['number', 'keyword', 'difficulty_level', 'search_volume', 'competition_level', 'explanation', 'article_idea_1', 'article_idea_2']],
                column_config={
                    "number": "No.",
                    "keyword": "Keyword",
                    "difficulty_level": "Difficulty",
                    "search_volume": "Est. Search Volume",
                    "competition_level": "Competition",
                    "explanation": "SEO Explanation",
                    "article_idea_1": "Content Idea 1",
                    "article_idea_2": "Content Idea 2"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Add download button
            medium_csv = st.session_state.generated_clusters['Medium'].to_csv(index=False)
            st.download_button(
                label="📥 Download Medium Difficulty Keywords",
                data=medium_csv,
                file_name=f"{topic.replace(' ', '_')}_medium_difficulty_keywords.csv",
                mime="text/csv",
                key="download_medium",
                use_container_width=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    with tab3:
        if st.session_state.generated_clusters['High'] is not None:
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.subheader(f"High Difficulty Keywords <span class='difficulty-badge high-difficulty'>Very Competitive</span>", unsafe_allow_html=True)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
            High difficulty keywords are highly competitive terms with strong traffic potential but difficult to rank for. 
            These typically require significant content investment and authority building but can yield substantial traffic if successfully ranked.
            """)
            
            # Display the DataFrame with enhanced styling
            st.dataframe(
                st.session_state.generated_clusters['High'][['number', 'keyword', 'difficulty_level', 'search_volume', 'competition_level', 'explanation', 'article_idea_1', 'article_idea_2']],
                column_config={
                    "number": "No.",
                    "keyword": "Keyword",
                    "difficulty_level": "Difficulty",
                    "search_volume": "Est. Search Volume",
                    "competition_level": "Competition",
                    "explanation": "SEO Explanation",
                    "article_idea_1": "Content Idea 1",
                    "article_idea_2": "Content Idea 2"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Add download button
            high_csv = st.session_state.generated_clusters['High'].to_csv(index=False)
            st.download_button(
                label="📥 Download High Difficulty Keywords",
                data=high_csv,
                file_name=f"{topic.replace(' ', '_')}_high_difficulty_keywords.csv",
                mime="text/csv",
                key="download_high",
                use_container_width=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Option to download all keywords at once
    if all(st.session_state.generated_clusters.values()):
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.subheader("Download All Keyword Data")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Combine all DataFrames into one
        all_df = pd.concat([
            st.session_state.generated_clusters['Low'],
            st.session_state.generated_clusters['Medium'],
            st.session_state.generated_clusters['High']
        ])
        
        # Add download button for all keywords
        all_csv = all_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Keywords (All Difficulty Levels)",
            data=all_csv,
            file_name=f"{topic.replace(' ', '_')}_all_keywords.csv",
            mime="text/csv",
            key="download_all",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content strategy recommendations
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.subheader("Content Strategy Recommendations")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### How to Use These Keywords in Your Content Strategy:
        
        1. **Build a Topic Cluster Structure:**
           - Use higher difficulty keywords as "pillar" content
           - Create supporting content using medium and low difficulty keywords
           - Interlink all related content pieces
        
        2. **Strategic Content Creation Order:**
           - Start with low difficulty keywords to gain initial traction
           - Progress to medium difficulty as your site authority grows
           - Target high difficulty keywords once you've established topical authority
        
        3. **Content Format Suggestions:**
           - Low Difficulty: How-to guides, tutorials, FAQs, specialized information
           - Medium Difficulty: Comprehensive guides, case studies, industry insights
           - High Difficulty: Definitive guides, original research, expert interviews
        
        4. **Publishing Cadence:**
           - Aim for at least 2-3 new content pieces weekly in the first months
           - Focus on quality and comprehensive coverage rather than quantity
           - Maintain a consistent publishing schedule
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add footer
st.markdown("""
<footer>
    <p>© 2023 Content Cluster Generator | Powered by OpenAI | Created with ❤️ using Streamlit</p>
</footer>
""", unsafe_allow_html=True)
