"""
Skill vocabularies and constants from all three branches
"""

# From main branch - General tech + EV skills
MAIN_SKILLS = [
    # Programming
    "Python", "C++", "C", "Java", "JavaScript", "TypeScript", "MATLAB", "R", "Rust",
    # EV / Hardware
    "EV", "Electric Vehicle", "Battery", "BMS", "Motor Control", "Inverter",
    "Charging", "CAN Bus", "BLDC", "PMSM", "Regenerative Braking",
    # Embedded / IoT
    "Arduino", "Raspberry Pi", "STM32", "ESP32", "RTOS", "Embedded Systems",
    "Firmware", "Microcontroller", "PCB", "KiCad", "Altium",
    # CAD / Simulation
    "SolidWorks", "AutoCAD", "CATIA", "Fusion 360", "ANSYS", "CAD", "CAE",
    "FEA", "CFD", "LTspice",
    # Data / ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Data Analysis", "SQL", "Power BI", "Tableau",
    # Web / Cloud
    "React", "Node.js", "FastAPI", "Flask", "Django", "Docker", "AWS", "GCP",
    # Soft skills
    "Team Leadership", "Project Management", "Agile", "Research",
]

# From ev-hiring-platform - EV-specific taxonomy
EV_SKILLS = [
    # Battery
    'Battery Management', 'BMS', 'Lithium-ion', 'Solid State Battery',
    'Battery Thermal Management', 'Cell Balancing', 'State of Charge',
    # Powertrain
    'Electric Motor', 'Inverter', 'Converter', 'Powertrain',
    'Regenerative Braking', 'Traction Control', 'Differential',
    # Charging
    'EV Charging', 'Fast Charging', 'Wireless Charging', 'CCS', 'CHAdeMO',
    'Type 2 Connector', 'V2G', 'Bidirectional Charging',
    # Software & Controls
    'CAN Bus', 'AUTOSAR', 'MATLAB', 'Simulink', 'Vector CANoe',
    'Model Based Design', 'Embedded C', 'ASPICE', 'ISO 26262',
    # Vehicle Systems
    'ADAS', 'Autonomous Driving', 'Sensor Fusion', 'LIDAR', 'Radar',
    'Camera Systems', 'Path Planning', 'Vehicle Dynamics',
    # Protocols
    'ISO 15118', 'DIN 70121', 'OCPP', 'MQTT', 'WebSocket',
    # Cloud & Telematics
    'AWS IoT', 'Azure IoT', 'Google Cloud', 'Telematics', 'Fleet Management',
    # Testing
    'HIL Testing', 'SIL Testing', 'MIL Testing', 'dSPACE', 'NI LabVIEW',
    # Core Engineering
    'Python', 'C++', 'Java', 'Control Systems', 'Power Electronics',
    'PCB Design', 'EMC/EMI', 'Thermal Management',
]

# From shashwat - VisionAstraa-specific skills
VISIONASTRAA_SKILLS = {
    "api design", "aws", "azure", "cloud computing", "css",
    "data engineering", "docker", "fastapi", "flask", "gcp",
    "git", "html", "javascript", "kubernetes", "llm",
    "machine learning", "microservices", "mongodb",
    "natural language processing", "nlp", "postgresql",
    "prompt engineering", "python", "react", "rest api",
    "sql", "tensorflow", "transformers", "typescript",
    "vector database",
}

# EV-domain skill weights (from ev-hiring-platform)
SKILL_WEIGHTS = {
    'battery management': 3, 'bms': 3, 'lithium-ion': 2, 'solid state battery': 3,
    'battery thermal management': 2, 'cell balancing': 2,
    'electric motor': 2, 'inverter': 2, 'powertrain': 2, 'regenerative braking': 2,
    'ev charging': 2, 'fast charging': 2, 'ccs': 2, 'chademo': 2, 'v2g': 3,
    'can bus': 3, 'autosar': 3, 'matlab': 2, 'simulink': 2, 'iso 26262': 3,
    'aspice': 2, 'embedded c': 2, 'model based design': 2,
    'adas': 3, 'autonomous driving': 3, 'sensor fusion': 3, 'lidar': 2, 'radar': 2,
    'hil testing': 2, 'sil testing': 2, 'dspace': 2,
    'python': 1, 'c++': 1, 'java': 1, 'power electronics': 2,
}

# Resume validation patterns (from shashwat)
RESUME_SECTION_HEADERS = {
    "experience", "education", "skills", "work history",
    "employment", "qualifications", "projects", "certifications",
    "achievements", "accomplishments", "professional summary",
    "career objective", "technical skills", "core competencies",
}

RESUME_KEYWORDS = {
    "developed", "managed", "led", "created", "implemented",
    "engineer", "developer", "analyst", "architect", "designer",
    "university", "bachelor", "master", "gpa", "project", "team",
    "responsible", "achieved", "improved", "built", "designed",
    "programmed", "coded", "maintained", "deployed", "collaborated",
}

# Fake data patterns (from shashwat)
FAKE_EMAIL_PATTERNS = {
    "test@test.com", "example@domain.com", "fake@fake.com",
    "123@456.com", "a@b.com", "test@example.com",
    "user@test.com", "demo@demo.com",
}

FAKE_PHONE_PATTERNS = {
    "123-456-7890", "111-111-1111", "000-000-0000",
    "555-555-5555", "1234567890", "1111111111",
    "(123) 456-7890", "(111) 111-1111", "(555) 555-5555",
}

FAKE_NAMES = {
    "john doe", "jane doe", "test user", "fake user",
    "john smith", "jane smith", "test test", "demo user",
}

# Expected MIME types (from shashwat)
EXPECTED_MIME = {
    "pdf": {"application/pdf"},
    "txt": {"text/plain", "application/octet-stream"},
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    },
}

# Default Job Description (from main)
DEFAULT_JD = """VisionAstraa EV Academy is looking for passionate interns to work on electric vehicle
technology, battery systems, motor control, and EV software. Candidates should have knowledge
of Python, embedded systems, or CAD/CAE tools. Experience with Arduino, Raspberry Pi,
or EV components is a plus. Strong problem-solving skills and enthusiasm for sustainable
transportation required."""

DEFAULT_JD_SKILLS = [
    "Python", "EV", "Arduino", "Raspberry Pi", "CAD", "Battery",
    "Motor Control", "Embedded Systems", "C++", "MATLAB", "SolidWorks"
]
