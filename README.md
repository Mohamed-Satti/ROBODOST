# 🤖 ROBODOST

**Companion Robot for Disabled Users (All Age Groups)**

ROBODOST is a localized, multimodal companion robot built for real-time interaction using ROS2 Humble on an NVIDIA Jetson Orin Nano Super. Designed with safety and accessibility at its core, it supports Turkish sign language processing, responsive speech pipelines, and physical mechatronic control.

## 📖 Key Features
* **Local-First AI**: Runs a compact 3B-parameter quantized LLM (via llama.cpp) entirely on-edge.
* **Multimodal Context**: Fuses audio inputs (Whisper ASR) and visual context (YOLOv8 & MediaPipe) into a rolling contextual snapshot.
* **Dual-Path Emergency Safety**: Hardware-level power cutoff coupled instantly with software-level event suppression.
* **Accessibility Focused**: "Visual Wake Words" for hearing-impaired users and continuous facial expression tracking interactions.

## 📂 Documentation Hub
For a full breakdown of the robotics pipeline, consult strings the `docs/` dictionary:
- [System Architecture](docs/architecture.md) - Node mapping, data streams, and safe-execution pipeline.
- [Workspace & File Structure](docs/file_structure.md) - Navigating the ROS2 packages and source files.

## 🚀 Quick Start (Development)

### Windows / Local AI Testing (No ROS)
To rapidly test standard AI pipeline logic natively on your laptop, navigate to any package's `core/` folder (e.g., `src/robodost_hri/robodost_hri/core/`). These act as Pure-Python sandboxes that decouple hard AI pipelines (like YOLO and Whisper) from ROS networking constraints. Run your virtual environment locally and test your logic using the localized pipeline scripts you build (like `speech_pipeline.py` or `vision_pipeline.py`) before migrating the logic into ROS 2 nodes.

### Full System Deployment (ROS 2 / Jetson)
1. Navigate to the deployment utility folder:
   ```bash
   cd system_deploy/
   ```
2. Install required ROS2 dependencies and Python packages:
   ```bash
   ./install_deps.sh
   ```
3. Initialize the hardware USB aliases (Linux/Jetson only):
   ```bash
   sudo ./create_udev_rules.sh
   ```
4. Build the ROS2 workspace locally:
   ```bash
   cd ~/robodost_ws
   colcon build --symlink-install
   source install/setup.bash
   ```
5. Launch the primary stack test:
   ```bash
   ros2 launch robodost_bringup system_local.launch.py
   ```
