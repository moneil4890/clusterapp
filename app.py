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
        
        # Filter to ensure we have exactly 1-2 word keywords
        valid_keywords = []
        for _, row in df.iterrows():
            keyword = row['keyword'].strip()
            word_count = len(keyword.split())
            
            if word_count <= 2:
                valid_keywords.append(row)
        
        # If we don't have enough valid keywords, this attempt failed
        if len(valid_keywords) < 20:
            return None
        
        # Take exactly 20 valid keywords
        valid_df = pd.DataFrame(valid_keywords[:20])
        
        # Add a numbered index starting from 1
        valid_df = valid_df.reset_index().rename(columns={"index": "number"})
        valid_df['number'] = valid_df['number'] + 1  # Start numbering from 1 instead of 0
        
        return valid_df
    
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
    st.rerun()  # Force UI update to show progress
    
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
        st.rerun()  # Force UI update
        
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
        st.rerun()  # Force UI update
        
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
            st.session_state.generation_progress['status'] = 'warning'
    
    # Set the final status
    remaining_overlaps = sum(check_keyword_distinctness(all_clusters)[0].values())
    if remaining_overlaps > 0:
        st.session_state.generation_progress['message'] = f"Completed with {remaining_overlaps} remaining keyword overlaps. You may regenerate for better results."
    else:
        st.session_state.generation_progress['message'] = "Successfully generated distinct keyword sets for all difficulty levels!"
    
    st.session_state.generation_progress['status'] = 'completed'
    return all_clusters
# Process form submission
if submit_button:
    if not topic:
        st.error("Please enter a main topic of interest.")
    else:
        # Reset attempt counts
        st.session_state.generation_progress['attempt_count'] = {
            'Low': 0,
            'Medium': 0,
            'High': 0
        }
        
        # Generate clusters for all difficulties
        with st.spinner("Generating content clusters across all difficulty levels..."):
            all_clusters = generate_all_content_clusters(topic, max_retries)
            
            if all_clusters:
                # Store the results in session state
                st.session_state.generated_clusters = all_clusters
                st.session_state.last_topic = topic
                
                # Calculate final keyword sets
                _, final_keywords = check_keyword_distinctness(all_clusters)
                st.session_state.all_keywords = final_keywords
                
                # Reset the selected tab to "Low" for new results
                st.session_state.selected_tab = "Low"
                
                # Show success message
                st.markdown("""
                <div class="success-message">
                    <h3>✅ Content clusters generated successfully!</h3>
                    <p>Your content clusters for <strong>{}</strong> are ready. 
                    Browse through the different difficulty levels using the tabs below.</p>
                </div>
                """.format(topic), unsafe_allow_html=True)
                
                # Track successful generation (could be used for analytics)
                if 'generation_history' not in st.session_state:
                    st.session_state.generation_history = []
                
                # Add this topic to history with timestamp
                st.session_state.generation_history.append({
                    'topic': topic,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'keyword_counts': {
                        diff: len(keywords) for diff, keywords in final_keywords.items()
                    },
                    'overlaps': sum(check_keyword_distinctness(all_clusters)[0].values())
                })
                
                # If we've reached our generation limit, we could show a message
                # This can be used if you want to implement usage limits
                # if len(st.session_state.generation_history) >= MAX_GENERATIONS:
                #     st.warning("You've reached your daily generation limit. Please try again tomorrow.")
            else:
                # Handle the case where generation failed
                st.error("Failed to generate content clusters. Please try again with a different topic or adjust parameters.")
                
                # If we have specific error information, display it
                if st.session_state.generation_error:
                    st.markdown(f"""
                    <div class="retry-card">
                        <h4>Error Details:</h4>
                        <p>{st.session_state.generation_error}</p>
                        <p>Suggestions:</p>
                        <ul>
                            <li>Try a more specific or different topic</li>
                            <li>Check your internet connection</li>
                            <li>Increase the maximum retry attempts</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)


# Display progress and status updates
if st.session_state.generation_progress['status'] != 'idle':
    status = st.session_state.generation_progress['status']
    
    # Display progress section
    st.markdown('<div class="progress-section">', unsafe_allow_html=True)
    
    # Status message
    if status == 'generating':
        st.markdown(f"### 🔄 Generation in Progress")
        st.markdown(f"**Current Task:** {st.session_state.generation_progress['message']}")
        
        # Show difficulty progress
        current_difficulty = st.session_state.generation_progress['current_difficulty']
        if current_difficulty:
            st.markdown(f"**Generating:** {current_difficulty} Difficulty Keywords")
            st.markdown(f"**Attempt:** {st.session_state.generation_progress['attempt_count'][current_difficulty]} of {max_retries}")
            
            # Add a progress bar based on current difficulty level
            difficulties = ["Low", "Medium", "High"]
            progress = (difficulties.index(current_difficulty) + 0.5) / len(difficulties)
            st.progress(progress)
    
    elif status == 'completed':
        st.markdown(f"### ✅ Generation Complete")
        st.markdown(f"**Status:** {st.session_state.generation_progress['message']}")
        
        # Show keyword statistics
        overlaps, keywords = check_keyword_distinctness(st.session_state.generated_clusters)
        total_overlaps = sum(overlaps.values())
        
        st.markdown("### Keyword Statistics")
        st.markdown('<div class="keyword-stats">', unsafe_allow_html=True)
        
        # Display keyword counts per difficulty
        for difficulty in ['Low', 'Medium', 'High']:
            st.markdown(f"""
            <div class="keyword-stat">
                <div class="keyword-count">{len(keywords[difficulty])}</div>
                <div class="keyword-label">{difficulty} Keywords</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Display overlap information
        st.markdown(f"""
        <div class="keyword-stat">
            <div class="keyword-count">{total_overlaps}</div>
            <div class="keyword-label">Keyword Overlaps</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display specific overlap details
        if total_overlaps > 0:
            st.markdown("#### Overlap Details:")
            for overlap_type, count in overlaps.items():
                if count > 0:
                    difficulty1, difficulty2 = overlap_type.split('_')
                    st.markdown(f"- {count} overlaps between {difficulty1} and {difficulty2} difficulty")
    
    elif status == 'error':
        st.markdown('<div class="retry-card">', unsafe_allow_html=True)
        st.markdown("### ❌ Generation Error")
        st.markdown(f"**Error:** {st.session_state.generation_error}")
        st.markdown("Please try again with a different topic or check your API connection.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display generated clusters if available
if st.session_state.generated_clusters['Low'] is not None:
    st.markdown(f"## Content Clusters for: {st.session_state.last_topic}")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Create tabs for different difficulty levels
    st.markdown('<div class="difficulty-tabs">', unsafe_allow_html=True)
    tab_options = ["Low", "Medium", "High"]
    
    # Create columns for the tabs
    tab_cols = st.columns(len(tab_options))
    
    # Default to Low difficulty if no tab is selected
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = "Low"
    
    # Display tabs
    for i, tab in enumerate(tab_options):
        with tab_cols[i]:
            if st.button(f"{tab} Difficulty", key=f"tab_{tab}", 
                         help=f"View {tab} difficulty keywords"):
                st.session_state.selected_tab = tab
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected difficulty info card
    selected_tab = st.session_state.selected_tab
    difficulty_params = get_difficulty_parameters(selected_tab)
    
    # Assign appropriate CSS class for the active tab
    tab_class = ""
    if selected_tab == "Low":
        tab_class = "active-low"
    elif selected_tab == "Medium":
        tab_class = "active-medium"
    else:
        tab_class = "active-high"
    
    # Update tab styling based on selection
    tab_html = '<div class="difficulty-tabs">'
    for tab in tab_options:
        class_name = f"difficulty-tab active-{tab.lower()}" if tab == selected_tab else "difficulty-tab"
        tab_html += f'<div class="{class_name}">{tab} Difficulty</div>'
    tab_html += '</div>'
    
    st.markdown(tab_html, unsafe_allow_html=True)
    
    # Display info card for the selected difficulty
    st.markdown(f"""
    <div class="info-card">
        <h3>{selected_tab} Difficulty Keywords <span class="difficulty-badge {selected_tab.lower()}-difficulty">{selected_tab}</span></h3>
        <p><strong>Description:</strong> {difficulty_params['description']}</p>
        <p><strong>Search Volume:</strong> {difficulty_params['search_volume']}</p>
        <p><strong>Competition:</strong> {difficulty_params['competition']}</p>
        <p><strong>Examples:</strong> {difficulty_params['examples']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display cluster results for selected tab
    if st.session_state.generated_clusters[selected_tab] is not None:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        # Format the DataFrame for better display
        display_df = st.session_state.generated_clusters[selected_tab].copy()
        
        # Reorder and rename columns for better display
        display_columns = {
            'number': '#',
            'keyword': 'Keyword',
            'search_volume': 'Search Volume',
            'competition_level': 'Competition',
            'explanation': 'Why This Difficulty Level',
            'article_idea_1': 'Content Idea 1',
            'article_idea_2': 'Content Idea 2'
        }
        
        # Select and reorder columns if they exist
        cols_to_display = [col for col in display_columns.keys() if col in display_df.columns]
        display_df = display_df[cols_to_display]
        
        # Rename columns
        display_df = display_df.rename(columns={k: v for k, v in display_columns.items() if k in display_df.columns})
        
        st.dataframe(display_df, use_container_width=True)
        
        # Add download button for current tab
        csv = display_df.to_csv(index=False)
        st.download_button(
            label=f"Download {selected_tab} Difficulty Keywords",
            data=csv,
            file_name=f"{st.session_state.last_topic.replace(' ', '_')}_{selected_tab}_keywords.csv",
            mime="text/csv",
            key=f"download_{selected_tab}"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add a button to download all difficulty levels
        st.markdown("### Download All Difficulty Levels")
        
        all_dfs = []
        for diff in tab_options:
            if st.session_state.generated_clusters[diff] is not None:
                temp_df = st.session_state.generated_clusters[diff].copy()
                temp_df['difficulty'] = diff  # Add the difficulty level as a column
                all_dfs.append(temp_df)
        
        if all_dfs:
            combined_df = pd.concat(all_dfs)
            combined_csv = combined_df.to_csv(index=False)
            
            st.download_button(
                label="Download All Keywords (Combined CSV)",
                data=combined_csv,
                file_name=f"{st.session_state.last_topic.replace(' ', '_')}_all_keywords.csv",
                mime="text/csv",
                key="download_all"
            )

# Add a footer
st.markdown('<footer>', unsafe_allow_html=True)
st.markdown('© 2023 Content Cluster Generator | Created with ❤️ by SEO Pros')
st.markdown('</footer>', unsafe_allow_html=True)
