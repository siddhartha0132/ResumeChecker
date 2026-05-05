"""
EV Industry Knowledge Base
Documents ingested into ChromaDB for RAG context during scoring
"""

from typing import Dict

# ── Knowledge documents ───────────────────────────────────────────────────────

EV_KNOWLEDGE_DOCS: Dict[str, str] = {
    "battery_engineering": """
BATTERY ENGINEER RESUME EVALUATION GUIDE

Key Technical Skills to Look For:
- Battery Management Systems (BMS): cell balancing, SoC/SoH estimation, thermal runaway protection
- Lithium-ion cell chemistry: NMC, LFP, NCA, solid-state
- Thermal management: cooling systems, heat dissipation, pack design
- Battery pack integration: mechanical, electrical, software
- Safety testing: UN38.3, IEC 62133, thermal runaway, crush, penetration
- Simulation tools: MATLAB/Simulink, GT-Suite, ANSYS Fluent

Important Certifications:
- EV Battery Technician Certification (NPTEL / Coursera)
- High Voltage Safety Training (mandatory for hands-on roles)
- ISO 26262 Functional Safety (for BMS software roles)

Recommended Experience Levels:
- Intern/Fresher: Academic projects with BMS, Arduino-based battery monitors
- Junior (1-3 yrs): Industry BMS development, cell testing, pack assembly
- Senior (4+ yrs): Full pack design, thermal management, safety validation

Red Flags:
- No hands-on battery or high-voltage experience
- Missing safety training for hands-on roles
- No understanding of cell chemistry or thermal management
- Claiming BMS experience without any supporting projects

Scoring Guidance:
- 90-100: Strong BMS + thermal + safety + relevant industry experience
- 75-89: Good BMS knowledge, some gaps in thermal or safety
- 60-74: Basic battery knowledge, needs development
- Below 60: Significant gaps, not suitable for battery-specific roles
""",

    "powertrain_engineering": """
POWERTRAIN ENGINEER RESUME EVALUATION GUIDE

Key Technical Skills to Look For:
- Electric motor design: PMSM, BLDC, induction motors
- Power electronics: inverters, converters, gate drivers
- Motor control algorithms: FOC, DTC, SVPWM
- Regenerative braking systems and energy recovery
- Drivetrain integration: transmission, differential, torque vectoring
- Simulation: MATLAB/Simulink, Ansys Maxwell, JMAG, dSPACE

Important Tools & Standards:
- Vector CANoe / CANalyzer for CAN bus testing
- dSPACE / NI HIL for hardware-in-loop testing
- AUTOSAR for embedded software architecture
- ISO 26262 for functional safety

Recommended Experience:
- 4+ years for senior roles in electric powertrain development
- Experience with motor control algorithms and efficiency optimization
- Knowledge of drive cycle analysis (WLTP, NEDC, EPA)

Interview Validation Questions:
- How do you size a motor for a given vehicle specification?
- Explain your approach to efficiency optimization across a drive cycle
- How do you handle torque ripple in PMSM control?

Scoring Guidance:
- 90-100: Motor control + power electronics + HIL testing + AUTOSAR
- 75-89: Good motor knowledge, some gaps in embedded or testing
- 60-74: Basic powertrain knowledge
- Below 60: Not suitable for powertrain-specific roles
""",

    "charging_infrastructure": """
CHARGING INFRASTRUCTURE EXPERT RESUME EVALUATION GUIDE

Key Technical Skills:
- AC/DC charging standards: CCS (Combo 1/2), CHAdeMO, GB/T, Type 2
- Communication protocols: ISO 15118 (Plug & Charge, V2G), OCPP 1.6/2.0
- Grid integration: load management, demand response, smart charging
- Electrical infrastructure: switchgear, transformers, protection systems
- V2G (Vehicle-to-Grid) and bidirectional charging
- Network management: CSMS, OCPI, OCPP backend

Important Certifications:
- EVSE Installation Certification (NICEIC / EV Association)
- Electrical Safety Certificate (18th Edition Wiring Regulations)
- Grid Integration Specialist

Key Projects to Highlight:
- Number of charging stations deployed
- Load balancing implementations
- Integration with energy management systems
- V2G pilot projects

Scoring Guidance:
- 90-100: Multiple standards + OCPP + grid integration + V2G experience
- 75-89: Good charging knowledge, some gaps in grid or protocols
- 60-74: Basic charging infrastructure knowledge
- Below 60: Not suitable for charging-specific roles
""",

    "adas_autonomy": """
ADAS / AUTONOMY ENGINEER RESUME EVALUATION GUIDE

Key Technical Skills:
- Sensor technologies: LiDAR, RADAR, cameras, ultrasonic
- Sensor fusion: Kalman filter, particle filter, deep learning fusion
- Perception: object detection (YOLO, SSD), semantic segmentation
- Path planning: A*, RRT, model predictive control
- Localization: SLAM, HD maps, GPS/IMU fusion
- Programming: C++17, Python, ROS/ROS2, CUDA

Important Frameworks & Tools:
- ROS / ROS2 for robotics middleware
- CARLA, LGSVL for simulation
- TensorFlow / PyTorch for deep learning
- Autoware, Apollo for autonomous driving stacks

Safety Standards:
- ISO 26262 (Functional Safety)
- ISO 21448 (SOTIF - Safety of the Intended Functionality)
- MISRA C++ for safety-critical code

Scoring Guidance:
- 90-100: Sensor fusion + perception + planning + safety standards + C++
- 75-89: Good perception or planning, some gaps
- 60-74: Basic ADAS knowledge
- Below 60: Not suitable for ADAS-specific roles
""",

    "embedded_software": """
EMBEDDED SOFTWARE ENGINEER RESUME EVALUATION GUIDE

Key Technical Skills:
- Embedded C/C++ for microcontrollers (ARM Cortex-M, STM32, ESP32)
- RTOS: FreeRTOS, Zephyr, QNX, AUTOSAR OS
- Communication protocols: CAN, LIN, SPI, I2C, UART, Ethernet
- AUTOSAR architecture: SWC, RTE, BSW, MCAL
- Functional safety: ISO 26262, MISRA C, ASPICE
- Debugging: JTAG, oscilloscope, logic analyzer, Vector CANoe

Important Certifications:
- AUTOSAR Fundamentals (Vector Academy)
- ISO 26262 Functional Safety Engineer
- ASPICE Assessor / Practitioner

Key Indicators of Quality:
- Experience with safety-critical embedded systems
- Knowledge of MISRA C/C++ coding standards
- HIL/SIL testing experience
- Code review and static analysis (LDRA, Polyspace)

Scoring Guidance:
- 90-100: AUTOSAR + ISO 26262 + CAN + RTOS + safety-critical experience
- 75-89: Good embedded skills, some gaps in AUTOSAR or safety
- 60-74: Basic embedded knowledge
- Below 60: Not suitable for safety-critical embedded roles
""",

    "resume_best_practices": """
EV INDUSTRY RESUME BEST PRACTICES

What Makes a Strong EV Resume:

1. Technical Skills Section:
   - List specific EV technologies (BMS, CAN Bus, Inverter design, AUTOSAR)
   - Include proficiency level where relevant
   - Group by domain: Battery | Powertrain | Charging | Software | Testing

2. Experience Descriptions:
   - Use strong action verbs: Designed, Implemented, Optimized, Validated
   - Quantify achievements: "Reduced thermal runaway risk by 30%"
   - Mention specific EV projects and measurable outcomes
   - Include team size and your specific contribution

3. Certifications That Matter:
   - EV-related certifications carry significant weight
   - High voltage safety training is often mandatory for hardware roles
   - ISO 26262 / ASPICE for software/embedded roles

4. Projects Section:
   - Personal EV projects demonstrate genuine passion
   - Open source contributions to EV software (e.g., OpenBMS, OVMS)
   - Participation in EV competitions (Formula SAE Electric, Shell Eco-marathon)
   - GitHub links with actual code are highly valued

5. Keywords That Maximize ATS Score:
   - BMS, CAN, HIL, dSPACE, AUTOSAR, MATLAB/Simulink
   - ISO 26262, ASPICE, MISRA, Functional Safety
   - Python, C++, Embedded C, ROS, TensorFlow
   - Thermal management, Cell balancing, V2G, OCPP

6. Common Mistakes to Avoid:
   - Generic skills list without EV context
   - No quantified achievements
   - Missing relevant certifications
   - No GitHub or portfolio link
   - Spelling errors in technical terms (BMS ≠ BSM)

Scoring Benchmarks:
- 90-100%: Strong match on skills + experience + certifications + projects
- 75-89%: Good technical match, missing some desired skills
- 60-74%: Basic qualifications met, needs development in key areas
- Below 60%: Significant gaps in required skills
""",

    "visionastraa_culture": """
VISIONASTRAA EV ACADEMY — CULTURE & VALUES FIT GUIDE

About VisionAstraa:
VisionAstraa EV Academy trains the next generation of EV engineers through hands-on
programs in battery technology, motor control, charging infrastructure, and EV software.

What We Look For Beyond Technical Skills:

1. Passion for Sustainable Transportation:
   - Personal interest in EVs, clean energy, or climate tech
   - Side projects related to EVs or sustainability
   - Awareness of EV industry trends and challenges

2. Learning Agility:
   - Evidence of self-learning (online courses, certifications)
   - Ability to pick up new technologies quickly
   - Contributions to open source or community projects

3. Collaboration & Communication:
   - Team projects with clear individual contributions
   - Technical writing or documentation experience
   - Presentation or teaching experience

4. Problem-Solving Mindset:
   - Approach to debugging and root cause analysis
   - Experience with iterative design and prototyping
   - Comfort with ambiguity and fast-paced environments

5. Internship / Fresher Specific:
   - Academic projects with real hardware (Arduino, Raspberry Pi, STM32)
   - Participation in hackathons or competitions
   - Strong fundamentals in physics, math, and programming

Red Flags for Culture Fit:
- No evidence of passion for EVs or sustainability
- Only theoretical knowledge, no hands-on projects
- Poor communication in application materials
- Unrealistic salary expectations for entry-level roles
""",
}


async def ingest_knowledge_base(force: bool = False) -> Dict:
    """
    Ingest all EV knowledge documents into ChromaDB.
    Skips if already ingested (unless force=True).
    """
    from app.rag.vector_store import get_vector_store

    store = get_vector_store()

    # Skip if already ingested
    if not force and store.knowledge_count() > 0:
        return {
            "status": "skipped",
            "reason": "Knowledge base already ingested",
            "chunks": store.knowledge_count(),
        }

    ingested = 0
    for doc_id, content in EV_KNOWLEDGE_DOCS.items():
        store.add_knowledge_doc(
            doc_id=doc_id,
            text=content,
            metadata={"source": doc_id, "type": "ev_guidelines"},
        )
        ingested += 1

    return {
        "status": "success",
        "documents_ingested": ingested,
        "total_chunks": store.knowledge_count(),
    }
