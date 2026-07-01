import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ranking_engine.jd import analyze_job_description, load_job_description

# 1. MERN Stack Developer JD
mern_jd = """
MERN Stack Developer
We are looking for a Senior Developer to build web apps.
Required Skills: React, Node.js, Express, MongoDB, JavaScript, HTML, CSS.
Preferred: TypeScript, Tailwind, Next.js.
Requirements:
- 5 to 7 years of web development experience.
- Bachelor's degree in Computer Science.
- Excellent communication and team collaboration.
- Hybrid working mode in Bangalore.
- Build and optimize user-facing features.
"""

# 2. Java Backend Engineer JD
java_jd = """
Java Backend Engineer
Join our finance team to build backend services.
Required: Java, Spring Boot, MySQL, REST API, Git.
Preferred: Docker, Kubernetes, AWS.
Experience: 3-6 years.
Industry: Finance.
Role expectations: problem-solving, autonomy.
"""

# 3. DevOps Engineer JD
devops_jd = """
DevOps Engineer
Manage our cloud infrastructure and deployment pipelines.
Required: Docker, Kubernetes, Terraform, AWS, CI/CD, Linux.
Preferred: Ansible, Python, GitHub Actions.
Experience Required: 4+ years.
Behavioral: fast learner, startup mindset.
"""

# 4. Data Engineer JD
data_jd = """
Data Engineer
Build large scale data pipelines.
Required: Spark, Kafka, SQL, Python, Hadoop, ETL.
Preferred: Airflow, Snowflake, Redshift.
Experience: 5-8 years.
Industry: Retail.
Responsibilities:
- Build and own data pipelines and ETL processes.
"""

# 5. Frontend React Developer JD
frontend_jd = """
Frontend React Developer
Required: React, TypeScript, Redux, Sass, CSS3, HTML5.
Preferred: Tailwind, Next.js, Figma.
Experience: 2-4 years.
"""

def verify_all():
    print("--- 1. Redrob AI Engineer (Seeded) ---")
    ai_out = load_job_description()
    print(f"Role: {ai_out['role']}")
    print(f"Required Skills: {ai_out['required_skills']}")
    print(f"Experience Min/Max: {ai_out['experience_min']} - {ai_out['experience_max']}")
    assert ai_out['role'] == "AI Engineer" or ai_out['role'] == "research"
    assert "embeddings_retrieval" in ai_out['required_skills']
    assert "vector_search" in ai_out['required_skills']
    assert "python" in ai_out['required_skills']
    assert "ranking_evaluation" in ai_out['required_skills']
    
    print("\n--- 2. MERN Stack Developer ---")
    mern_out = analyze_job_description(mern_jd)
    print(f"Role: {mern_out['role']}")
    print(f"Required Skills: {mern_out['required_skills']}")
    print(f"Preferred Skills: {mern_out['preferred_skills']}")
    print(f"Experience Min/Max: {mern_out['experience_min']} - {mern_out['experience_max']}")
    assert mern_out['role'] == "Full Stack" or mern_out['role'] == "Frontend"
    assert "React" in mern_out['required_skills']
    assert "MongoDB" in mern_out['required_skills']
    assert "Next.js" in mern_out['preferred_skills']
    # Verify no fallback to AI-only keys if they aren't in JD
    assert "embeddings_retrieval" not in mern_out['required_skills']

    print("\n--- 3. Java Backend Engineer ---")
    java_out = analyze_job_description(java_jd)
    print(f"Role: {java_out['role']}")
    print(f"Required Skills: {java_out['required_skills']}")
    print(f"Preferred Skills: {java_out['preferred_skills']}")
    print(f"Experience Min/Max: {java_out['experience_min']} - {java_out['experience_max']}")
    assert java_out['role'] == "Backend"
    assert "Java" in java_out['required_skills']
    assert "Spring Boot" in java_out['required_skills']
    assert "AWS" in java_out['preferred_skills']

    print("\n--- 4. DevOps Engineer ---")
    devops_out = analyze_job_description(devops_jd)
    print(f"Role: {devops_out['role']}")
    print(f"Required Skills: {devops_out['required_skills']}")
    print(f"Preferred Skills: {devops_out['preferred_skills']}")
    print(f"Experience Min/Max: {devops_out['experience_min']} - {devops_out['experience_max']}")
    assert devops_out['role'] == "DevOps"
    assert "Docker" in devops_out['required_skills']
    assert "Terraform" in devops_out['required_skills']
    assert "Ansible" in devops_out['preferred_skills']

    print("\n--- 5. Data Engineer ---")
    data_out = analyze_job_description(data_jd)
    print(f"Role: {data_out['role']}")
    print(f"Required Skills: {data_out['required_skills']}")
    print(f"Preferred Skills: {data_out['preferred_skills']}")
    print(f"Experience Min/Max: {data_out['experience_min']} - {data_out['experience_max']}")
    assert data_out['role'] == "Data Engineering"
    assert "Spark" in data_out['required_skills']
    assert "Kafka" in data_out['required_skills']
    assert "Snowflake" in data_out['preferred_skills']

    print("\n--- 6. Frontend React Developer ---")
    front_out = analyze_job_description(frontend_jd)
    print(f"Role: {front_out['role']}")
    print(f"Required Skills: {front_out['required_skills']}")
    print(f"Preferred Skills: {front_out['preferred_skills']}")
    print(f"Experience Min/Max: {front_out['experience_min']} - {front_out['experience_max']}")
    assert front_out['role'] == "Frontend"
    assert "React" in front_out['required_skills']
    assert "TypeScript" in front_out['required_skills']
    assert "Next.js" in front_out['preferred_skills']

    print("\nAll parser verifications passed successfully!")

if __name__ == "__main__":
    verify_all()
