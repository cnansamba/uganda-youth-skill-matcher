import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Kampala Youth Skill Matcher + Dashboard")

# === 1. LOAD/GENERATE KAMPALA YOUTH DATA ===
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 150
    data = {
        'age': np.random.randint(18, 36, n),
        'gender': np.random.choice(['Male', 'Female'], n, p=[0.52, 0.48]),
        'division': np.random.choice(['Central', 'Nakawa', 'Makindye', 'Rubaga', 'Kawempe'], n),
        'employment_status': np.random.choice(['Employed', 'Unemployed', 'Student'], n, p=[0.3, 0.5, 0.2]),
        'digital_skills_score': np.random.randint(1, 11, n),
        'vocational_skill': np.random.choice(['Tailoring', 'Carpentry', 'Plumbing', 'Welding', 'Hair Dressing', 'Motor Repair'], n),
        'education_level': np.random.choice(['None', 'Primary', 'O-Level', 'A-Level', 'Certificate', 'Diploma', 'Degree'], n)
    }
    df = pd.DataFrame(data)
    return df

df = load_data()

# === 2. KAMPALA GEO DATA + HOTSPOTS ===
division_coords = {
    'Central': [0.3136, 32.5811],
    'Nakawa': [0.3322, 32.6138],
    'Makindye': [0.2667, 32.5833],
    'Rubaga': [0.3167, 32.5500],
    'Kawempe': [0.3667, 32.5500]
}

SKILL_HOTSPOTS = {
    "Kawempe": {"Boom Skill": "Boda Mechanic", "Reason": "High boda population, low mechanic density. Avg 200+ bodas need weekly service."},
    "Makindye": {"Boom Skill": "Hair & Beauty Tech", "Reason": "Growing middle class, 3+ new salons monthly. High event styling demand."},
    "Central": {"Boom Skill": "Phone Repair", "Reason": "CBD foot traffic 50k+/day. 1 in 3 phones need repair yearly."},
    "Nakawa": {"Boom Skill": "Furniture Maker", "Reason": "Ntinda-Bukoto housing boom. 500+ new apartments yearly need custom furniture."},
    "Rubaga": {"Boom Skill": "Tailor", "Reason": "Owino/Nateete markets. School uniforms + church wear constant demand."}
}

# === 3. REFERRAL INSTITUTIONS + QUALIFICATIONS ===
SCHOOLS = {
    "Tailor": {"name": "Management Training & Advisory Centre", "duration": "2 months", "cost": "400K UGX", "contact": "041-4-251481", "location": "Nakawa", "qualification": "Certificate in Tailoring", "education_required": "None"},
    "Hair & Beauty Tech": {"name": "Tina's School of Beauty", "duration": "6 weeks", "cost": "250K UGX", "contact": "0772-456-789", "location": "Wandegeya", "qualification": "Diploma in Cosmetology", "education_required": "Primary"},
    "Boda Mechanic": {"name": "Katwe Technical Institute", "duration": "1 month", "cost": "200K UGX", "contact": "0755-111-222", "location": "Katwe", "qualification": "Certificate in Motorcycle Repair", "education_required": "None"},
    "Catering & Food Safety": {"name": "Uganda Hotel & Tourism Training Institute", "duration": "3 months", "cost": "350K UGX", "contact": "041-xxx", "location": "Jinja Road", "qualification": "Certificate in Food Production", "education_required": "Primary"},
    "OBD-II Diagnostics": {"name": "Katwe Auto Academy", "duration": "2 weeks", "cost": "150K UGX", "contact": "0700-123-456", "location": "Katwe", "qualification": "Certificate in Auto Diagnostics", "education_required": "O-Level"},
    "Industrial Machine Repair": {"name": "Nakawa Vocational Training Institute", "duration": "3 months", "cost": "300K UGX", "contact": "0414-222-333", "location": "Nakawa", "qualification": "Certificate in Industrial Maintenance", "education_required": "A-Level"},
    "Furniture Maker": {"name": "Bwaise Carpentry School", "duration": "4 months", "cost": "450K UGX", "contact": "0777-333-444", "location": "Bwaise", "qualification": "Certificate in Carpentry", "education_required": "Primary"},
    "Metal Fabricator": {"name": "Kampala Polytechnic", "duration": "3 months", "cost": "400K UGX", "contact": "041-555-666", "location": "Old Kampala", "qualification": "Certificate in Welding", "education_required": "O-Level"},
    "Agro-Processing": {"name": "Makerere Agri-Business Incubator", "duration": "6 weeks", "cost": "200K UGX", "contact": "041-777-888", "location": "Makerere", "qualification": "Certificate in Food Processing", "education_required": "A-Level"},
    "Digital Marketing": {"name": "Outbox Hub", "duration": "1 month", "cost": "300K UGX", "contact": "039-999-000", "location": "Bugolobi", "qualification": "Certificate in Digital Marketing", "education_required": "A-Level"},
    "Phone Repair": {"name": "Cooper Complex Tech Hub", "duration": "1 month", "cost": "250K UGX", "contact": "0701-234-567", "location": "Central", "qualification": "Certificate in Phone Repair", "education_required": "O-Level"},
    "Junior Developer": {"name": "Refactory Academy", "duration": "3 months", "cost": "1.2M UGX", "contact": "039-111-222", "location": "Bugolobi", "qualification": "Certificate in Software Dev", "education_required": "A-Level"},
    "Electrician": {"name": "Nakawa Vocational Training Institute", "duration": "3 months", "cost": "350K UGX", "contact": "0414-222-333", "location": "Nakawa", "qualification": "Certificate in Electrical Installation", "education_required": "O-Level"},
    "Plumber": {"name": "Kampala Polytechnic", "duration": "3 months", "cost": "300K UGX", "contact": "041-555-666", "location": "Old Kampala", "qualification": "Certificate in Plumbing", "education_required": "Primary"},
    "Business Administration": {"name": "Makerere University Business School", "duration": "2 years", "cost": "2.5M UGX/yr", "contact": "041-xxx-xxx", "location": "Nakawa", "qualification": "Diploma in Business Admin", "education_required": "A-Level"}
}

# === EDUCATION_MATCH: CUMULATIVE ELIGIBLE + RECOMMENDED ===
EDUCATION_MATCH = {
    "None": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker"],
        "recommended": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker"],
        "message": "Vocational training recommended. Use personal interests to match skills."
    },
    "Primary": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber"],
        "recommended": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber"],
        "message": "Certificate programs are a good fit."
    },
    "O-Level": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician"],
        "recommended": ["OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician"],
        "message": "You qualify for most vocational certificates. Subject interests help specialization."
    },
    "A-Level": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician",
                     "Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "recommended": ["Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "message": "You qualify for advanced diplomas. Subject interests guide career path."
    },
    "Certificate": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician",
                     "Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "recommended": ["Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Business Administration", "Electrician"],
        "message": "Match to specific certificate studied."
    },
    "Diploma": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician",
                     "Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "recommended": ["Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "message": "Match to specific diploma studied."
    },
    "Degree": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician",
                     "Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "recommended": ["Digital Marketing", "Agro-Processing", "Business Administration", "Junior Developer"],
        "message": "Specify degree field for management/training roles."
    },
    "Masters": {
        "eligible": ["Tailor", "Boda Mechanic", "Hair & Beauty Tech", "Furniture Maker", "Catering & Food Safety", "Plumber",
                     "OBD-II Diagnostics", "Metal Fabricator", "Phone Repair", "Electrician",
                     "Industrial Machine Repair", "Digital Marketing", "Agro-Processing", "Junior Developer", "Business Administration"],
        "recommended": ["Digital Marketing", "Agro-Processing", "Business Administration", "Junior Developer", "Industrial Machine Repair"],
        "message": "Consider consulting, large-scale enterprise, or training others."
    }
}

DIVISION_DEMAND = {
    "Kawempe": {"Tailor": "High", "Hair & Beauty Tech": "Medium", "Industrial Machine Repair": "Low", "Boda Mechanic": "High", "Furniture Maker": "Medium", "Phone Repair": "Medium", "Electrician": "High", "Plumber": "High", "Business Administration": "Medium", "Junior Developer": "Low"},
    "Makindye": {"Tailor": "Medium", "Hair & Beauty Tech": "High", "Industrial Machine Repair": "Medium", "Boda Mechanic": "High", "Furniture Maker": "Low", "Phone Repair": "High", "Electrician": "Medium", "Plumber": "Medium", "Business Administration": "High", "Junior Developer": "Medium"},
    "Central": {"Tailor": "Low", "Hair & Beauty Tech": "High", "Industrial Machine Repair": "High", "Boda Mechanic": "Medium", "Furniture Maker": "Medium", "Phone Repair": "High", "Electrician": "High", "Plumber": "Medium", "Business Administration": "High", "Junior Developer": "High"},
    "Nakawa": {"Tailor": "Medium", "Hair & Beauty Tech": "Medium", "Industrial Machine Repair": "High", "Boda Mechanic": "Low", "Furniture Maker": "High", "Phone Repair": "Medium", "Electrician": "High", "Plumber": "Low", "Business Administration": "High", "Junior Developer": "Medium"},
    "Rubaga": {"Tailor": "High", "Hair & Beauty Tech": "Medium", "Industrial Machine Repair": "Low", "Boda Mechanic": "High", "Furniture Maker": "Medium", "Phone Repair": "Low", "Electrician": "Medium", "Plumber": "High", "Business Administration": "Medium", "Junior Developer": "Low"}
}

AVG_STARTUP_COST = {
    "Tailor": 500000, "Hair & Beauty Tech": 800000, "Industrial Machine Repair": 1500000,
    "Boda Mechanic": 600000, "OBD-II Diagnostics": 400000, "Catering & Food Safety": 300000,
    "Furniture Maker": 1200000, "Metal Fabricator": 900000, "Agro-Processing": 700000,
    "Digital Marketing": 200000, "Business Administration": 500000, "Phone Repair": 350000,
    "Junior Developer": 800000, "Electrician": 450000, "Plumber": 300000
}

EST_MONTHLY_PROFIT = {
    "Tailor": 250000, "Hair & Beauty Tech": 400000, "Industrial Machine Repair": 600000,
    "Boda Mechanic": 350000, "OBD-II Diagnostics": 300000, "Catering & Food Safety": 200000,
    "Furniture Maker": 500000, "Metal Fabricator": 450000, "Agro-Processing": 400000,
    "Digital Marketing": 350000, "Business Administration": 300000, "Phone Repair": 400000,
    "Junior Developer": 600000, "Electrician": 350000, "Plumber": 250000
}

MARKET_INSIGHTS = {
    "Tailor": "School uniform season Sept-Jan peaks. Church wear steady. Competition high near markets. Differentiate with custom designs.",
    "Hair & Beauty Tech": "Wedding season May-Dec busiest. Bridal makeup 150K-300K per client. Social media drives 70% of clients.",
    "Boda Mechanic": "Rainy seasons Mar-May, Sept-Nov spike repairs. 1 mechanic serves ~50 bodas. Spare parts margin 30-40%.",
    "Phone Repair": "Screen replacement 70% of jobs. CBD shops charge 20% more. Water damage spikes in rainy season.",
    "Furniture Maker": "Housing estates drive bulk orders. 1 bedroom set = 1.2M revenue. Material costs 60%.",
    "Industrial Machine Repair": "Factories pay retainers 500K-2M/month. Downtime costs them 5M+/day. Reliability > price.",
    "Catering & Food Safety": "Events peak Dec, Easter, weddings. Corporate lunch contracts = steady income 1M+/month.",
    "Agro-Processing": "Harvest seasons determine supply. Dry season = scarcity premium. UNBS certification opens supermarkets.",
    "Digital Marketing": "SMEs budget 200K-1M/month. Results-based contracts common. TikTok/WhatsApp Business hot channels.",
    "Junior Developer": "NGOs + startups pay 1.5M-3M/month. Mobile money integration high demand. Build portfolio first.",
    "Electrician": "New constructions + solar boom. House wiring 800K-2M. Solar install 15% commission.",
    "Plumber": "Estate maintenance contracts steady. Emergency call-outs 50K-150K. Water shortage = tank install boom.",
    "Metal Fabricator": "Gates/grills 300K-1.5M each. Construction sites bulk orders. Welding skill = price premium.",
    "OBD-II Diagnostics": "Modern cars 2010+ need computer diagnosis. 30K per scan. Partner with garages for referrals.",
    "Business Administration": "SMEs need bookkeeping, URA filing, staff management. Retainer 300K-800K/month."
}

OCCUPATION_SKILL_WEIGHTS = {
    "Business Administration": {"business": 0.4, "comm": 0.3, "digital": 0.2, "tech": 0.1},
    "Digital Marketing": {"digital": 0.4, "comm": 0.3, "business": 0.2, "tech": 0.1},
    "Junior Developer": {"digital": 0.5, "tech": 0.3, "business": 0.1, "comm": 0.1},
    "Phone Repair": {"tech": 0.5, "digital": 0.2, "business": 0.2, "comm": 0.1},
    "Electrician": {"tech": 0.6, "business": 0.2, "comm": 0.1, "digital": 0.1},
    "Plumber": {"tech": 0.6, "business": 0.2, "comm": 0.1, "digital": 0.1},
    "Tailor": {"tech": 0.5, "business": 0.3, "comm": 0.1, "digital": 0.1},
    "Hair & Beauty Tech": {"tech": 0.4, "comm": 0.3, "business": 0.2, "digital": 0.1},
    "Boda Mechanic": {"tech": 0.6, "business": 0.2, "comm": 0.1, "digital": 0.1},
    "Furniture Maker": {"tech": 0.6, "business": 0.2, "comm": 0.1, "digital": 0.1},
    "Metal Fabricator": {"tech": 0.6, "business": 0.2, "comm": 0.1, "digital": 0.1},
    "Industrial Machine Repair": {"tech": 0.5, "digital": 0.2, "business": 0.2, "comm": 0.1},
    "OBD-II Diagnostics": {"tech": 0.4, "digital": 0.3, "business": 0.2, "comm": 0.1},
    "Catering & Food Safety": {"tech": 0.3, "business": 0.3, "comm": 0.3, "digital": 0.1},
    "Agro-Processing": {"tech": 0.4, "business": 0.3, "comm": 0.2, "digital": 0.1}
}

OCCUPATION_PRIMARY_SKILL = {
    "Business Administration": "business", "Digital Marketing": "digital", "Junior Developer": "digital",
    "Phone Repair": "tech", "Electrician": "tech", "Plumber": "tech", "Tailor": "tech",
    "Hair & Beauty Tech": "tech", "Boda Mechanic": "tech", "Furniture Maker": "tech",
    "Metal Fabricator": "tech", "Industrial Machine Repair": "tech", "OBD-II Diagnostics": "tech",
    "Catering & Food Safety": "tech", "Agro-Processing": "tech"
}


# === 4. DASHBOARD SECTION ===
st.header("📊 Kampala Youth Skills Dashboard")

# === 4. DASHBOARD SECTION ===
st.header("📊 Kampala Youth Skills Dashboard")

# MOVE FILTER UP FIRST
st.subheader("Filter by Division")
selected_division_filter = st.selectbox("Choose division", df['division'].unique(), key="div_filter")
filtered_df = df[df['division'] == selected_division_filter]

# NOW CALCULATE KPIs FROM FILTERED_DF
col1, col2, col3 = st.columns(3)
col1.metric("Total Youth", len(filtered_df))
col2.metric("Unemployment Rate", f"{(filtered_df['employment_status'] == 'Unemployed').mean() * 100:.1f}%")
col3.metric("Avg Digital Skills", f"{filtered_df['digital_skills_score'].mean():.1f}/10")

# Then show the table
with st.expander("View Filtered Youth Data Table", expanded=False):
    st.dataframe(filtered_df, use_container_width=True, height=300)
    
st.divider()

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Employment Status Breakdown")
    fig = px.bar(
        filtered_df['employment_status'].value_counts().reset_index(),
        x='employment_status', y='count',
        labels={'employment_status': 'Employment Status', 'count': 'Number of Youth'},
        color='employment_status'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Youth Distribution + Skill Hotspots")
    
    # 1. CHECK: Do these exist? If not, error will happen here instead of later
    st.write("Debug - selected_division:", selected_division)
    st.write("Debug - filtered_df rows:", len(filtered_df))
    
    # 2. Imports - put these at TOP of your file, but adding here to be safe
    import folium
    from streamlit_folium import st_folium
    
    # 3. Define everything inside col_b so no scope issues
    division_coords = {
        'Makindye': [0.2765, 32.5880],
        'Rubaga': [0.3163, 32.5503], 
        'Kawempe': [0.3871, 32.5643],
        'Central': [0.3156, 32.5811],
        'Nakawa': [0.3329, 32.6256]
    }
    
    SKILL_HOTSPOTS = {
        'Makindye': {'Boom Skill': 'Digital Marketing', 'Reason': 'High youth + high unemployment'},
        'Kawempe': {'Boom Skill': 'Carpentry', 'Reason': 'Construction demand'},
        'Rubaga': {'Boom Skill': 'Tailoring', 'Reason': 'Textile market proximity'}
    }
    
    # 4. Only run map if selected_division is valid
    if selected_division in division_coords:
        m = folium.Map(location=[0.3476, 32.5825], zoom_start=12)
        
        div_count = len(filtered_df)
        folium.CircleMarker(
            location=division_coords[selected_division],
            radius=max(5, div_count/2),  # max(5, ...) prevents radius=0
            popup=f"{selected_division}: {div_count} youth",
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)
        
        if selected_division in SKILL_HOTSPOTS:
            folium.Marker(
                location=division_coords[selected_division],
                popup=f"<b>Hotspot:</b> {SKILL_HOTSPOTS[selected_division]['Boom Skill']}<br>{SKILL_HOTSPOTS[selected_division]['Reason']}",
                icon=folium.Icon(color='green', icon='star')
            ).add_to(m)
        
        st_folium(m, width=700, height=400)
    else:
        st.error(f"Division '{selected_division}' not found in coords. Check dropdown values.")
        
# === 5. SKILL MATCHER INPUTS - 6 SECTORS ===
st.markdown("---")
st.header("🎯 Individual Skill Matcher")

age = st.number_input("Age", 18, 35, 25)
education_level = st.selectbox(
    "Education Level",
    ["None", "Primary", "O-Level", "A-Level", "Certificate", "Diploma", "Degree", "Masters"]
)

degree_field = None
certificate_field = None
subject_interest = None
personal_interest = None

if education_level == "Degree" or education_level == "Masters":
    degree_field = st.text_input("Specify Degree Field", placeholder="e.g., Bachelor of Procurement, BSc Computer Science")
elif education_level == "Certificate" or education_level == "Diploma":
    certificate_field = st.selectbox("Specific Certificate/Diploma", ["Business Administration", "IT", "Accounting", "Electrical Installation", "Plumbing", "Other"])
    if certificate_field == "Other":
        certificate_field = st.text_input("Specify Certificate/Diploma")
elif education_level == "O-Level" or education_level == "A-Level":
    subject_interest = st.multiselect("Subject Interests", ["Math", "Physics", "Biology", "Chemistry", "Geography", "History", "Commerce", "Entrepreneurship", "ICT", "Art & Design"])
elif education_level == "None" or education_level == "Primary":
    personal_interest = st.multiselect("Personal Interests", ["Working with hands", "Talking to people", "Computers/Phones", "Cars/Bikes", "Cooking", "Drawing/Design", "Selling/Business", "Farming"])

division = st.selectbox(
    "Kampala Division",
    ["Makindye", "Central", "Kawempe", "Nakawa", "Rubaga"]
)
capital = st.number_input("Available Capital (UGX)", 0, 10000000, 500000)

tech_skill = st.slider("Technical/Trade Skills", 0, 10, 5)
digital_skill = st.slider("Digital Skills", 0, 10, 5)
comm_skill = st.slider("Communication Skills", 0, 10, 5)
business_skill = st.slider("Business Skills", 0, 10, 5)

sector_interest = st.selectbox(
    "Sector of Interest",
    ["Services", "Tech", "Agriculture", "Trade", "Manufacturing", "Retail"]
)

occupation = "None"
if sector_interest == "Services":
    occupation = st.selectbox("Target Occupation", ["None", "Tailor", "Hair & Beauty Tech", "Boda Mechanic", "Catering & Food Safety", "Electrician", "Plumber"])
elif sector_interest == "Tech":
    occupation = st.selectbox("Target Occupation", ["None", "Phone Repair", "Junior Developer", "Digital Marketing", "OBD-II Diagnostics"])
elif sector_interest == "Agriculture":
    occupation = st.selectbox("Target Occupation", ["None", "Agro-Processing"])
elif sector_interest == "Trade":
    occupation = st.selectbox("Target Occupation", ["None", "Business Administration"])
elif sector_interest == "Manufacturing":
    occupation = st.selectbox("Target Occupation", ["None", "Industrial Machine Repair", "Furniture Maker", "Metal Fabricator"])
elif sector_interest == "Retail":
    occupation = st.selectbox("Target Occupation", ["None", "Digital Marketing", "Business Administration"])

# === 6. 3-PANEL SKILL MATCHING OUTPUT ===
st.markdown("---")
st.subheader("Skill-Matching Results")
st.write(f"**Path:** {occupation if occupation!= 'None' else sector_interest} in {division}")

col1, col2, col3 = st.columns([1.2, 1, 1.2])

with col1:
    st.markdown("### 1. COMPREHENSIVE INPUT")
    st.markdown("**🎓 Education Match**")
    if education_level in EDUCATION_MATCH:
        eligible_skills = EDUCATION_MATCH[education_level]["eligible"]
        recommended_skills = EDUCATION_MATCH[education_level]["recommended"]
        st.success(EDUCATION_MATCH[education_level]["message"])

        if degree_field:
            st.info(f"**Degree:** {degree_field}")
        if certificate_field:
            st.info(f"**Certificate/Diploma:** {certificate_field}")
        if subject_interest:
            st.info(f"**Subjects:** {', '.join(subject_interest)}")
        if personal_interest:
            st.info(f"**Interests:** {', '.join(personal_interest)}")

        st.markdown("**⭐ Recommended for your education level:**")
        st.caption(f"{', '.join(recommended_skills)}")

        with st.expander("See all eligible skills"):
            st.caption(f"{', '.join(eligible_skills)}")

        if occupation!= 'None':
            required_edu = SCHOOLS[occupation].get('education_required', 'None')
            edu_levels = ["None", "Primary", "O-Level", "A-Level", "Certificate", "Diploma", "Degree", "Masters"]
            if education_level in ["Masters", "Degree", "Diploma"] and required_edu in ["None", "Primary", "O-Level"]:
                if occupation not in recommended_skills:
                    st.warning(f"⚠️ **Overqualified:** {occupation} only requires {required_edu}. With {education_level}, consider: {', '.join(recommended_skills[:3])}. You'll still need the technical certificate.")
            elif occupation not in eligible_skills:
                st.warning(f"⚠️ {occupation} typically requires different education. Consider: {', '.join(recommended_skills[:3])}")

    st.markdown("**👤 Your Profile**")
    st.write(f"Age: {age}")
    st.write(f"Education: {education_level}")
    st.write(f"Division: {division}")
    st.write(f"Capital: {capital:,} UGX")

    st.markdown("**📊 Current Skills**")
    st.progress(tech_skill / 10, text=f"Technical/Trade: {tech_skill}/10")
    st.progress(digital_skill / 10, text=f"Digital: {digital_skill}/10")
    st.progress(comm_skill / 10, text=f"Communication: {comm_skill}/10")
    st.progress(business_skill / 10, text=f"Business: {business_skill}/10")

with col2:
    st.markdown("### 2. VIABILITY PREDICTION")

    if occupation!= 'None' and occupation in OCCUPATION_SKILL_WEIGHTS:
        weights = OCCUPATION_SKILL_WEIGHTS[occupation]
        skill_scores = {
            "tech": tech_skill, "digital": digital_skill,
            "comm": comm_skill, "business": business_skill
        }
        weighted_skill_score = sum(skill_scores[skill] * weight for skill, weight in weights.items()) * 10
    else:
        weighted_skill_score = (tech_skill + digital_skill + comm_skill + business_skill) * 2.5

    viability_score = weighted_skill_score
    if occupation!= 'None' and occupation in AVG_STARTUP_COST:
        capital_factor = min(capital / AVG_STARTUP_COST[occupation], 1.0) * 20
        viability_score = viability_score * 0.7 + capital_factor * 0.3

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=viability_score,
        domain={'x': [0, 1], 'y': [0, 1]}, title={'text': "Viability Score"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#1f77b4"}, 'steps': [
            {'range': [0, 50], 'color': "lightgray"},
            {'range': [50, 80], 'color': "yellow"},
            {'range': [80, 100], 'color': "lightgreen"}]}
    ))
    st.plotly_chart(fig, use_container_width=True)

    if division in SKILL_HOTSPOTS:
        hotspot_skill = SKILL_HOTSPOTS[division]['Boom Skill']
        hotspot_reason = SKILL_HOTSPOTS[division]['Reason']
        if occupation == 'None':
            st.info(f"🔥 **Hotspot in {division}:** {hotspot_skill}\n\n{hotspot_reason}")
        elif occupation == hotspot_skill:
            st.success(f"🔥 **Perfect Match!** {hotspot_skill} is booming in {division}\n\n{hotspot_reason}")

with col3:
    st.markdown("### 3. STRATEGIC OUTPUTS")
    if occupation!= 'None' and occupation in SCHOOLS:
        school = SCHOOLS[occupation]
        user_edu_levels = ["None", "Primary", "O-Level", "A-Level", "Certificate", "Diploma", "Degree", "Masters"]
        required_edu = school.get('education_required', 'None')
        edu_met = user_edu_levels.index(education_level) >= user_edu_levels.index(required_edu)

        primary_skill_type = OCCUPATION_PRIMARY_SKILL.get(occupation, "tech")
        primary_skill_value = {
            "tech": tech_skill, "digital": digital_skill,
            "comm": comm_skill, "business": business_skill
        }[primary_skill_type]

        skill_gap = primary_skill_value < 6

        if skill_gap or not edu_met:
            st.markdown(f"**Skill/Education Gap:** {occupation}")
            if not edu_met:
                st.error(f"⚠️ **Education Required:** {required_edu}. You have: {education_level}")
            if skill_gap:
                st.error(f"⚠️ **{primary_skill_type.title()} Skill Gap:** You have {primary_skill_value}/10. Aim for 6+ for {occupation}.")
            st.info(f"""
            **Institution:** {school['name']}
            **Duration:** {school['duration']}
            **Cost:** {school['cost']}
            **Location:** {school['location']}
            **Qualification:** {school.get('qualification', 'Certificate')}
            **Min. Education:** {required_edu}
            **Contact:** {school['contact']}
            """)
        else:
            st.success(f"**Skills + Education Match:** You meet the requirements for {occupation}.")

        st.markdown("**📈 Market Insights:**")
        if division in DIVISION_DEMAND and occupation in DIVISION_DEMAND[division]:
            demand = DIVISION_DEMAND[division][occupation]
            demand_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(demand, "⚪")
            st.write(f"{demand_color} **Demand in {division}:** {demand}")

        if occupation in MARKET_INSIGHTS:
            st.caption(MARKET_INSIGHTS[occupation])

        st.markdown("**💰 Financial Simulator:**")
        if occupation in AVG_STARTUP_COST:
            startup_cost = AVG_STARTUP_COST[occupation]
            monthly_profit = EST_MONTHLY_PROFIT.get(occupation, 300000)
            capital_gap = startup_cost - capital

            st.write(f"**Est. Startup Cost:** {startup_cost:,} UGX")
            st.write(f"**Your Capital:** {capital:,} UGX")
            st.write(f"**Est. Monthly Profit:** {monthly_profit:,} UGX")

            if capital_gap > 0:
                st.warning(f"**Capital Gap:** {capital_gap:,} UGX")
                months_to_fund = capital_gap / monthly_profit if monthly_profit > 0 else 0
                st.write(f"💡 **Funding Plan:** Save {monthly_profit:,} UGX/month from other work for ~{months_to_fund:.1f} months to cover gap.")
            else:
                surplus = abs(capital_gap)
                st.success(f"**Capital Surplus:** {surplus:,} UGX")

                if monthly_profit > 0:
                    breakeven_months = startup_cost / monthly_profit
                    st.write(f"📊 **Break-Even:** ~{breakeven_months:.1f} months to recover startup cost")

                st.write("**💡 Best Use of Surplus Capital:**")
                if surplus >= 1000000:
                    st.write("1. **Bulk inventory/materials:** Buy 3-6 months stock at wholesale. Saves 15-25%.")
                    st.write("2. **Better equipment:** Upgrade tools = faster service = more clients/day.")
                    st.write("3. **Marketing:** 200K-500K for signage, social media ads, launch promo.")
                elif surplus >= 300000:
                    st.write("1. **Marketing:** Signage + WhatsApp Business + 1 month Facebook ads.")
                    st.write("2. **Extra stock:** 2-3 months of fast-moving supplies to avoid stockouts.")
                    st.write("3. **Emergency fund:** Keep 100K for repairs/unexpected costs.")
                else:
                    st.write("1. **Keep as working capital:** Covers first month rent, utilities, small emergencies.")
                    st.write("2. **Small marketing:** Printed flyers + airtime for customer calls.")
    else:
        st.info("Select a Target Occupation to see skill-matching, market insights, and financial projections.")
