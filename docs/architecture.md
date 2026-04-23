# ROBODOST System Architecture

Target System: **NVIDIA Jetson Orin Nano Super (8GB)**  
Middleware: **ROS2 Humble**

## 1. High-Level Node Layout

The architecture is explicitly decoupled into five major computational domains. Communication follows an asynchronous publish-subscribe model via custom messages configured in `robodost_msgs`.

1. **HRI (Human-Robot Interaction)**: Captures audio -> triggers Silero VAD -> routes to `faster-whisper-tiny` (INT8) -> decodes text. System output maps text chunks straight to Piper streaming TTS for low perceptual latency.
2. **Vision Pipeline (CV)**: USB frame ingestion -> YOLOv8-nano Object Detection via TensorRT. MediaPipe tracks gestures for the isolated Turkish Sign Language 20-word command dictionary.
3. **Intelligence Hub (LLM)**: Unifies text analysis via a generic Inference Engine (toggled between a quantized 3B local model or an OpenAI wrapper).
4. **Core System (Integration)**: Defines the reality of the robot via the continuous Context Snapshot, oversees FSM execution, and forces degraded fallbacks via the Watchdog.
5. **Mechatronics**: Serial UART bridge transmitting hard real-time PID execution payloads directly to the Arduino Nano controller.

## 2. Asynchronous Context Store

To prevent CPU lockups when evaluating vision and audio cross-references, `context_store_node` maintains an **Append-Only Ring Buffer** in memory (a standard Python `deque`). 
- Generates a consolidated snapshot (Last 3 conversational turns + Latest Vision Bounding Boxes + System Telemetry) on `/context/snapshot` at 2Hz.
- The LLM assesses this environment snapshot dynamically upon receiving a user prompt without ever blocking the camera loop.

## 3. The Orchestrator FSM

The Orchestrator defines what actions the robot is allowed to physically execute. 
* **State Machine Flow**: `IDLE -> LISTENING -> PROCESSING -> EXECUTING -> IDLE`
* **Preemption/Barge-in**: If a visual wake word or auditory keyword interrupts while in `EXECUTING` (Robot is talking/moving), it drops the current routine, mutes the TTS engine, and halts Mechatronics. 

## 4. Hardware Fallback Subsystems (Watchdog)

Addressing the strict 8GB shared-RAM limit, the system monitors heartbeat packets to avoid cascading failure:
- **Mode 0 (Full AI)**: Llama/Qwen + YOLO + HRI Online.
- **Mode 1 (Cloud Fallback)**: Shifts inference payload to Cloud Endpoint if local GPU RAM exceeds 90% or the local node crashes.
- **Mode 2 (Minimal Survival)**: Vision & LLM disabled; System relies exclusively on hard-coded Regex ASR commands (e.g., "STOP").

## 5. Dual-Path Emergency Priority

1. **Hardware Path**: Analog physical red button directly cuts off external Li-ion battery power via Relay module to the MOSFET motor drivers. This guarantees instant stoppage.
2. **Software Path**: Triggering the button simultaneously registers an interrupt directly on the Jetson GPIO pin. The `emergency_node` instantly flags `/emergency/status = true`. The Orchestrator intercepts this globally and cancels all active motion queues.
