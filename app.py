import streamlit as st
import base64
from gemini_backend import analyze_resume, suggest_improvements, find_jobs

# --- Page Configuration ---
st.set_page_config(
    page_title="HireMe AI - Premium",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS (Premium Navy/White Theme) ---
st.markdown("""
<style>
    /* Global Font & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #1e293b;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom Navbar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: white;
        color: #1e293b;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 0;
    }
    .nav-logo { 
        font-size: 1.8rem; 
        font-weight: 700; 
        color: #1e293b;
    }
    .nav-logo span { 
        color: #4f46e5; 
    }

    /* Navigation Buttons */
    .nav-button {
        background: transparent !important;
        color: #64748b !important;
        border: none !important;
        font-weight: 500;
        padding: 8px 16px;
    }
    .nav-button:hover {
        color: #4f46e5 !important;
        background: #f8fafc !important;
    }

    /* Cards & Containers */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.2s;
        padding: 12px 24px;
    }
    
    /* Primary Button Style (Indigo) */
    .primary-btn button {
        background-color: #4f46e5 !important;
        color: white !important;
        border: none;
        font-size: 16px;
    }
    .primary-btn button:hover {
        background-color: #4338ca !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* Secondary Button Style */
    .secondary-btn button {
        background-color: white !important;
        color: #374151 !important;
        border: 2px solid #e5e7eb !important;
        font-size: 16px;
    }
    .secondary-btn button:hover {
        border-color: #4f46e5 !important;
        color: #4f46e5 !important;
        transform: translateY(-1px);
    }

    /* Feature Cards */
    .feature-card {
        background: white;
        border: 1px solid #f1f5f9;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #e2e8f0;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Hero Section */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        color: #1e293b;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    .accent-text {
        color: #4f46e5;
    }
            /* Home Page Buttons Fix */
.stButton > button {
    min-height: 50px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
}

/* Ensure all buttons have same height */
[data-testid="baseButton-secondary"] {
    min-height: 50px !important;
}

[data-testid="baseButton-primary"] {
    min-height: 50px !important;
}

            /* Simple Button Fix */
.stButton > button {
    min-height: 60px !important;
    font-size: 14px !important;
    line-height: 1.2 !important;
    padding: 10px 5px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
}
            
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 4rem;
    }

    /* Utility Classes */
    .text-center { text-align: center; }
    .mt-2 { margin-top: 2rem; }
    .mb-2 { margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'page' not in st.session_state:
    st.session_state.page = 'HOME'
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'improvements' not in st.session_state:
    st.session_state.improvements = []
if 'job_results' not in st.session_state:
    st.session_state.job_results = None
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False

# --- Navigation Component ---
def render_navbar():
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    with col1:
        st.markdown('<div class="nav-logo">HireMe<span>AI</span></div>', unsafe_allow_html=True)
    with col2:
        if st.button("Home", key="nav_home", use_container_width=True): 
            st.session_state.page = 'HOME'
    with col3:
        if st.button("Analysis", key="nav_analysis", use_container_width=True): 
            st.session_state.page = 'ANALYSIS'
    with col4:
        if st.button("Templates", key="nav_templates", use_container_width=True): 
            st.session_state.page = 'TEMPLATES'
    with col5:
        if st.button("Jobs", key="nav_jobs", use_container_width=True): 
            st.session_state.page = 'JOBS'
    
    st.markdown("<div style='height: 1px; background: #e2e8f0; margin-top: 10px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

render_navbar()

# --- Helper: Render HTML Template ---
# --- Helper: Render HTML Template ---
def get_template_html(template_id, data):
    name = data.get('name', 'Candidate Name')
    role = data.get('suggestedRole', 'Professional Role')
    summary = data.get('summary', '')
    skills = data.get('skillsFound', [])
    strengths = data.get('strengths', [])
    
    base_style = "padding: 40px; font-family: sans-serif; color: #1e293b; background: white; min-height: 1000px;"
    
    if template_id == "modern":
        return f"""
        <div id="resume-preview" style="{base_style}">
            <div style="border-bottom: 2px solid #0f172a; padding-bottom: 20px; margin-bottom: 30px;">
                <h1 style="font-size: 42px; margin: 0; text-transform: uppercase; letter-spacing: 1px;">{name}</h1>
                <p style="font-size: 18px; color: #64748b; margin-top: 10px;">{role}</p>
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 40px;">
                <div>
                    <h3 style="font-size: 14px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;">Professional Summary</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{summary}</p>
                    
                    <h3 style="font-size: 14px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-top: 30px;">Strengths</h3>
                    <ul style="font-size: 14px; line-height: 1.6;">
                        {''.join([f'<li>{s}</li>' for s in strengths])}
                    </ul>
                </div>
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                    <h3 style="font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 15px;">Skills</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        {''.join([f'<span style="background: white; border: 1px solid #e2e8f0; padding: 4px 8px; font-size: 12px;">{s}</span>' for s in skills])}
                    </div>
                </div>
            </div>
        </div>
        """
    elif template_id == "executive":
        return f"""
        <div id="resume-preview" style="{base_style} font-family: 'Georgia', serif; text-align: center;">
            <h1 style="font-size: 36px; color: #1e3a8a; margin-bottom: 5px;">{name}</h1>
            <p style="font-size: 16px; font-style: italic; color: #64748b; margin-bottom: 40px;">{role}</p>
            
            <div style="text-align: left; margin-bottom: 30px;">
                <h2 style="font-size: 16px; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px;">EXECUTIVE SUMMARY</h2>
                <p style="font-size: 14px; line-height: 1.8;">{summary}</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; text-align: left;">
                <div>
                    <h2 style="font-size: 16px; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px;">COMPETENCIES</h2>
                    <ul style="font-size: 14px; line-height: 1.6;">{''.join([f'<li>{s}</li>' for s in skills[:8]])}</ul>
                </div>
                 <div>
                    <h2 style="font-size: 16px; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px;">HIGHLIGHTS</h2>
                    <ul style="font-size: 14px; line-height: 1.6;">{''.join([f'<li>{s}</li>' for s in strengths])}</ul>
                </div>
            </div>
        </div>
        """
    elif template_id == "creative":
        return f"""
        <div id="resume-preview" style="{base_style} font-family: 'Arial', sans-serif;">
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 40px; margin: -40px -40px 40px -40px;">
                <h1 style="font-size: 48px; margin: 0; font-weight: 300;">{name}</h1>
                <p style="font-size: 20px; margin: 10px 0 0 0; opacity: 0.9;">{role}</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                <div>
                    <h3 style="font-size: 18px; color: #4f46e5; border-left: 4px solid #4f46e5; padding-left: 15px; margin-bottom: 20px;">PROFILE</h3>
                    <p style="font-size: 14px; line-height: 1.6; color: #64748b;">{summary}</p>
                    
                    <h3 style="font-size: 18px; color: #4f46e5; border-left: 4px solid #4f46e5; padding-left: 15px; margin: 30px 0 20px 0;">STRENGTHS</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        {''.join([f'<span style="background: #f1f5f9; color: #4f46e5; padding: 8px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{s}</span>' for s in strengths])}
                    </div>
                </div>
                
                <div>
                    <h3 style="font-size: 18px; color: #4f46e5; border-left: 4px solid #4f46e5; padding-left: 15px; margin-bottom: 20px;">SKILLS</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        {''.join([f'<span style="background: #4f46e5; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;">{s}</span>' for s in skills])}
                    </div>
                </div>
            </div>
        </div>
        """
    return "<div>Template not found</div>"

# --- VIEW: HOME ---

if st.session_state.page == 'HOME':
    
    # Hero Section
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="hero-title">Professional Resumes<br><span class="accent-text">Built by Intelligence</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Upload your CV, get AI-powered improvements, apply premium templates, and match with top-tier jobs instantly.</div>', unsafe_allow_html=True)
        
        # Buttons - FIXED SIZE & ALIGNMENT
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col1:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Enhance My Resume", use_container_width=True, key="home_enhance"):
                st.session_state.page = 'ANALYSIS'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col2:
            st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
            if st.button("View Templates", use_container_width=True, key="home_templates"):
                st.session_state.page = 'TEMPLATES'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col3:
            st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
            if st.button("Find Jobs", use_container_width=True, key="home_jobs"):
                st.session_state.page = 'JOBS'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Hero Image/Illustration
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 1rem; padding: 3rem; color: white;">
                <h2 style="margin: 0; font-size: 1.5rem;">AI-Powered Resume Builder</h2>
                <p style="opacity: 0.9; margin: 1rem 0 0 0;">Smart. Professional. Effective.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Features Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Deep Analysis</div>
            <div class="feature-desc">Get a detailed score and actionable feedback on your current resume with AI-powered insights.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✨</div>
            <div class="feature-title">AI Enhancement</div>
            <div class="feature-desc">Automatically rewrite weak bullet points and optimize content to sound more professional.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Matching</div>
            <div class="feature-desc">Find jobs that perfectly match your newly identified skills and experience.</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        © 2024 HireMe AI. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# --- VIEW: ANALYSIS ---
elif st.session_state.page == 'ANALYSIS':
    st.title("Resume Analysis")
    
    # Upload Section
    uploaded_file = st.file_uploader("Upload your Resume (PDF or Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    if uploaded_file and not st.session_state.resume_data:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("Analyze Resume", use_container_width=True):
            with st.spinner("Analyzing with Gemini 2.5..."):
                bytes_data = uploaded_file.getvalue()
                mime_type = uploaded_file.type
                result = analyze_resume(bytes_data, mime_type)
                if result:
                    st.session_state.resume_data = result
                    st.rerun()
                else:
                    st.error("Analysis failed. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results Section
    if st.session_state.resume_data:
        data = st.session_state.resume_data
        
        # Reset Button
        if st.button("Upload New Resume"):
            st.session_state.resume_data = None
            st.session_state.improvements = []
            st.rerun()

        # Editable Fields - FIXED VERSION
        with st.expander("✏️ Edit Profile Details", expanded=True):
            # Create a form to handle the save functionality
            with st.form("edit_profile_form"):
                new_name = st.text_input("Candidate Name", 
                                       value=data.get('name', ''), 
                                       key="edit_name")
                new_role = st.text_input("Target Role", 
                                       value=data.get('suggestedRole', ''), 
                                       key="edit_role")
                new_summary = st.text_area("Professional Summary", 
                                         value=data.get('summary', ''), 
                                         height=150, 
                                         key="edit_summary")
                
                # Save Changes Button inside form
                submitted = st.form_submit_button("💾 Save Changes")
                
            # Handle form submission
            if submitted:
                st.session_state.resume_data['name'] = new_name
                st.session_state.resume_data['suggestedRole'] = new_role
                st.session_state.resume_data['summary'] = new_summary
                st.success("✅ Changes saved successfully!")

        # Score & Highlights
        col1, col2 = st.columns([1, 2])
        with col1:
            score = data.get('score', 0)
            color = "#059669" if score > 70 else "#d97706" if score > 40 else "#dc2626"
            st.markdown(f"""
            <div style="text-align:center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <h1 style="font-size: 60px; color: {color}; margin: 0;">{score}</h1>
                <p style="color: #64748b; font-weight: bold;">ATS SCORE</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Detected Strengths")
            for s in data.get('strengths', []):
                st.success(s)

        # Weaknesses & Improvements
        st.markdown("### Areas for Improvement")
        weaknesses = data.get('weaknesses', [])
        
        for i, w in enumerate(weaknesses):
            with st.container():
                st.warning(w)
        
        if not st.session_state.improvements and weaknesses:
            if st.button("✨ Generate AI Improvements", key="generate_improvements"):
                with st.spinner("Thinking..."):
                    imps = suggest_improvements(weaknesses)
                    st.session_state.improvements = imps
                    st.rerun()
        
        if st.session_state.improvements:
            st.markdown("### AI Suggestions")
            for imp in st.session_state.improvements:
                st.info(f"💡 {imp}")

# --- VIEW: TEMPLATES ---

elif st.session_state.page == 'TEMPLATES':
    st.title("Premium Templates")
    
    if not st.session_state.resume_data:
        st.warning("Please analyze a resume first to use templates.")
        if st.button("Go to Analysis"):
            st.session_state.page = 'ANALYSIS'
            st.rerun()
    else:
        st.markdown("### Choose a Template Style")
        st.markdown("Select a template to preview your resume with professional formatting.")
        
        col1, col2, col3 = st.columns(3)
        
        template_choice = None
        
        with col1:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>Modern Tech</h3>
            </div>
            """, unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&q=80&w=400&h=300", 
                    caption="Clean & Professional", use_container_width=True)  # CHANGE HERE
            if st.button("Select Modern", key="modern_btn", use_container_width=True): 
                template_choice = "modern"
        
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>Executive Pro</h3>
            </div>
            """, unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1586282391129-76a6df840fd0?auto=format&fit=crop&q=80&w=400&h=300", 
                    caption="Elegant & Corporate", use_container_width=True)  # CHANGE HERE
            if st.button("Select Executive", key="executive_btn", use_container_width=True): 
                template_choice = "executive"

        with col3:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>Creative</h3>
            </div>
            """, unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?auto=format&fit=crop&q=80&w=400&h=300", 
                    caption="Modern & Creative", use_container_width=True)  # CHANGE HERE
            if st.button("Select Creative", key="creative_btn", use_container_width=True): 
                template_choice = "creative"

        if template_choice:
            st.session_state.selected_template = template_choice
            st.success(f"✅ {template_choice.title()} template selected! Preview below.")

        if 'selected_template' in st.session_state:
            st.markdown("---")
            st.subheader("Live Preview")
            st.info("💡 To download: Right-click inside the preview area → Print → Save as PDF")
            
            html_content = get_template_html(st.session_state.selected_template, st.session_state.resume_data)
            st.components.v1.html(html_content, height=1000, scrolling=True)

# --- VIEW: JOBS ---

elif st.session_state.page == 'JOBS':
    st.title("Smart Job Matching")
    
    if not st.session_state.resume_data:
        st.warning("⚠️ Please analyze your resume first to get personalized job matches!")
        if st.button("Go to Analysis"):
            st.session_state.page = 'ANALYSIS'
            st.rerun()
    else:
        # User's Profile Summary
        st.subheader("🎯 Your Profile Summary")
        data = st.session_state.resume_data
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Target Role", data.get('suggestedRole', 'Not specified'))
        with col2:
            st.metric("Skills Found", len(data.get('skillsFound', [])))
        with col3:
            score = data.get('score', 0)
            color = "green" if score > 70 else "orange" if score > 40 else "red"
            st.metric("Resume Score", f"{score}/100")
        
        # Auto-filled Job Search based on resume
        st.subheader("🔍 Find Jobs Matching Your Profile")
        
        with st.form("job_search"):
            # Auto-fill from resume data
            default_role = data.get('suggestedRole', '')
            skills = data.get('skillsFound', [])
            
            # SIMPLIFIED QUERY - Only use clean job title
            smart_query = default_role
            
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                query = st.text_input("Job Title", value=smart_query, 
                                    placeholder="e.g. Frontend Developer")
                st.caption("💡 Based on your resume analysis")
            with c2:
                loc = st.text_input("Location", placeholder="e.g. Remote, New York")
            with c3:
                mode = st.selectbox("Job Type", ["Any", "Remote", "Hybrid", "On-site"])
            
            # Smart search suggestions
            with st.expander("💡 Search Options"):
                st.write(f"**Your Skills:** {', '.join(skills[:5])}")
                st.write("**Try these variations:**")
                if default_role:
                    st.write(f"- `{default_role}`")
                    st.write(f"- `{default_role} {loc if loc else 'Remote'}`")
                    if skills:
                        st.write(f"- `{skills[0]} Developer`")
            
            search_submitted = st.form_submit_button("🚀 Find Matching Jobs")
        
        if search_submitted:
            with st.spinner("🔍 Searching for jobs that match your profile..."):
                # Use only the clean job title for search
                clean_query = query.split(',')[0].split(' with ')[0].strip()
                results = find_jobs(clean_query, loc, mode)
                st.session_state.job_results = results
        
        if st.session_state.job_results:
            res = st.session_state.job_results
            
            # AI Summary
            with st.expander("📊 AI Job Market Insights", expanded=True):
                st.write(res['text'])
            
            # Job Cards
            st.subheader(f"🎯 Found {len(res['sources'])} Opportunities")
            
            for i, job in enumerate(res['sources']):
                st.markdown(f"""
                <div style="padding: 20px; background: white; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #1e293b;">{job['title']}</h3>
                    <p style="margin: 5px 0; color: #64748b; font-size: 14px;">{job['company']}</p>
                    <a href="{job['url']}" target="_blank" style="display: inline-block; margin-top: 10px; text-decoration: none; color: #4f46e5; font-weight: 600;">View Job &rarr;</a>
                </div>
                """, unsafe_allow_html=True)
        
        # Manual override option
        st.markdown("---")
        st.subheader("🔧 Not Finding Right Jobs?")
        st.warning("If the auto-detected role doesn't match your expectations, you can:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit My Target Role", use_container_width=True):
                st.session_state.page = 'ANALYSIS'
                st.rerun()
        with col2:
            if st.button("🔄 Re-analyze Resume", use_container_width=True):
                st.session_state.resume_data = None
                st.session_state.page = 'ANALYSIS'
                st.rerun()