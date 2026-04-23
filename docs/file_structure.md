# ROS2 Workspace File Structure

ROBODOST employs a **"Package-per-Team"** design to ensure isolated development, prevent code-merge conflicts, and allow node clusters to be scaled dynamically based on system memory constraints.

## Directory Outline

```text
robodost_ws/
├── src/
│   ├── robodost_msgs/                 # Global API Contract (Team Integration)
│   │   ├── msg/                       # Custom topics (VisionUpdate, SpeechText)
│   │   └── srv/                       # Custom services (LLMQuery)
│   │
│   ├── robodost_hri/                  # Team C: Audio & User Interface
│   │   ├── wakeword_node.py
│   │   ├── asr_node.py
│   │   └── tts_node.py
│   │
│   ├── robodost_vision/               # Team B: Camera, YOLO, OCR, MediaPipe
│   │   ├── yolo_node.py
│   │   └── sign_language_node.py
│   │
│   ├── robodost_llm/                  # Team A: Reasoning and Text Engine
│   │   ├── llm_node.py                # Generic OpenAI Client Interface
│   │   └── config/llm_params.yaml     # Mode-toggle (use_cloud=true/false)
│   │
│   ├── robodost_core/                 # System Integration (Brain Stem)
│   │   ├── orchestrator_node.py       # FSM Action Engine
│   │   ├── context_store_node.py      # Snapshot Assembler
│   │   └── watchdog_node.py           # Heartbeat Degraded Modes Setup
│   │
│   ├── robodost_mechatronics/         # Team E: Arduino Comms & Kinematics
│   │   ├── hardware_bridge_node.py
│   │   └── firmware/arduino_controller/
│   │
│   └── robodost_bringup/              # Launch Orchestration
│       ├── launch/system_local.launch.py
│       ├── launch/system_full.launch.py
│       └── launch/system_minimal.launch.py
│
├── system_deploy/                     # Dependency management & UDEV scripts
└── docs/                              # Project Architecture Documents
```

## Why this specific framework?

1. **`robodost_msgs` Dependency Anchor**: The cross-team dependency. Before complex coding begins, teams must mutually agree on variable arrays in these `*.msg` schemas. This enables Team A to write `yolo_node.py` mocked-outputs while waiting for team B to develop the rest.
2. **Launch Composability**: The `robodost_bringup` package behaves as the global conductor. By writing distinct launch parameters (`system_local.launch.py`), we establish completely isolated operational scopes tailored for either lightweight testing or heavy-duty grading demonstrations.
