# problem Statement 2 : Gamified Learning Environment for AgentX

Build a gamified environment or simulation where AgentX can train, evolve, and demonstrate intelligent behavior.
Examples include: Puzzle-solving worlds Resource-optimization challenges Maze navigation User-engagement gamification platforms

## 🚀 Team: Power House
* **Members:** T. Jaswanth Kumar Reddy, Kuravi Charan Teja
* **Full Details:** See [TEAM.md](TEAM.md)

---

## 🎮 Game Modes

### 1. Survivor Mode (PVE)
* **Role:** You play as the **Survivor**.
* **Objective:** Collect all keys (Yellow Orbs) and reach the Exit (Green Box).
* **Enemy:** A **Hunter Agent** (AI) patrols the map and learns your movement patterns to catch you.
* **Abilities:** Sprint (Shift).

### 2. Hunter Mode (EVP)
* **Role:** You play as the **Hunter**.
* **Objective:** Catch the Survivor before they escape.
* **Enemy:** A **Survivor Agent** (AI) that scavenges for keys and uses smart evasion tactics.
* **Abilities:** Place Traps (Q), Scan Area (E).

### 3. Spectator / Training Mode (AVA)
* **Role:** Observer (God Mode).
* **Action:** Watch two AI agents (Hunter vs. Survivor) play against each other.
* **Purpose:** Rapidly train the Q-Learning models.
* **Features:**
    * No Fog of War.
    * Free Camera Movement.
    * **Time Scaling:** Speed up simulation up to 10x.

---

## ⌨️ Controls

| Context | Key | Action |
| :--- | :--- | :--- |
| **Menu** | `1`, `2`, `3` | Select Game Mode |
| **General** | `ESC` | Return to Menu / Quit |
| **Movement** | `W`, `A`, `S`, `D` or Arrows | Move Character |
| **Survivor** | `L-SHIFT` | Sprint (Consumes Stamina) |
| **Hunter** | `Q` | Place Trap |
| **Hunter** | `E` | Radar Scan (Reveal Survivor) |
| **Spectator** | `+` / `=` | Increase Simulation Speed |
| **Spectator** | `-` | Decrease Simulation Speed |
| **Dashboard** | `TAB` | Toggle Analysis View (Hunter/Survivor) |
| **Dashboard** | `Space` | Start Next Match |
| **Dashboard** | `Arrows` | Scroll History Replay |

---
## 🔬 Approach & Architecture

Our solution addresses the "Black Box" problem in Reinforcement Learning by creating a **Hybrid Neuro-Symbolic Architecture**. Instead of training agents purely on raw pixels (which is computationally expensive and slow), we decouple high-level strategy from low-level execution.

### 1. The Environment (Pygame Simulation)
* **Grid-Based World:** The map is quantized into a tilemap where `0 = Floor`, `1 = Wall`.
* **Sensory System (Fog of War):** We implemented a custom **Raycasting Algorithm** that limits the agent's vision cone. This forces the agents to learn "memory" and exploration strategies rather than reacting to perfect information.
* **Dynamic Elements:** The environment supports interactive entities like Traps (dynamic obstacles) and Doors (state changers).

### 2. The Agent Brain (Hybrid Q-Learning)
We use a hierarchical decision-making process:
* **Layer 1: The Executive (Q-Learning):**
    * The agent observes a **Discrete State** (e.g., `Enemy_Near`, `Stamina_Low`, `Can_See_Target`).
    * It queries a **Q-Table** to select a high-level *Intent* (e.g., "Retreat", "Chase", "Place Trap").
* **Layer 2: The Navigator (A* Pathfinding):**
    * Once an intent is formed, the agent uses **A* Pathfinding** to execute the movement efficiently.
    * This hybrid approach allows the agent to learn *strategy* in minutes rather than hours.

### 3. The Training Flow
1.  **Observation:** Agent scans radius using Raycasting.
2.  **Action Selection:** Epsilon-Greedy policy (Exploration vs. Exploitation).
3.  **Execution:** Action is performed; Physics engine updates positions.
4.  **Reward Shaping:**
    * **Hunter:** Positive reward for reducing distance to Survivor; Large reward for Trap triggers.
    * **Survivor:** Positive reward for "Unseen" time; Large reward for Keys.
5.  **Optimization:** Q-Values are updated using the Bellman Equation at every tick.
---
## 🧠 AI Architecture & Approach
The agents use a **Hybrid Q-Learning** approach with a lookup table to make decisions based on:
1.  **State Mapping:** (Patrolling, Chasing, Evading, Scavenging).
2.  **Sensory Input:** Ray-casting for walls and A* Pathfinding for distance calculation.
3.  **Memory:** Agents build a "heatmap" of visited locations to encourage exploration vs. exploitation.

**Persistence:**
The "Brains" (`hunter_qtable.pkl` and `survivor_qtable.pkl`) are saved automatically after every match in the `data/brains/` folder.

---

## 📊 Analytics Dashboard (Results)
After every match (or by pressing `TAB`), the **Dashboard** visualizes the training progress:
* **Movement Graph:** Tracks the total distance covered by agents to measure efficiency.
* **Decision Log:** Shows the exact "thought process" (e.g., `TRAP_SUCCESS`, `KEY_COLLECTED`) and the reward value assigned.
* **XP & Level:** Displays the agent's growth and "level up" status based on cumulative rewards.
* **Replay System:** Re-watch the previous match pathing on the mini-map.

---

## 📂 Project Structure

```text
AGENTX/
├── assets/          # Sprites (Survivor, Hunter) and Audio (MP3/WAV)
├── data/
│   ├── brains/      # Saved Q-Tables (.pkl files)
│   └── levels/      # Level layout configurations
├── engine/          # Core Game Engine
│   ├── dashboard.py # Analytics & Graphs
│   ├── tilemap.py   # Rendering Logic
│   └── ...
├── main.py          # Entry Point
├── requirements.txt # Dependencies
├── TEAM.md          # Team Details
└── README.md        # Documentation

```
## 🎯 Expected Outputs & Deliverables

### 1. Functional Simulation
* **Playable Game:** A bug-free, interactive application running at 60 FPS.
* **Dual Perspectives:** Users can experience the game as both predator (Hunter) and prey (Survivor).

### 2. Observable AI Evolution
* **Early Episodes (0-50):** Agents move randomly, hitting walls or getting caught easily.
* **Mid Training (50-200):** Agents begin using map geometry (corners) and retreating when stamina is low.
* **Expert Level (200+):**
    * **Hunter:** Predicts survivor pathing and places traps at choke points.
    * **Survivor:** Baits the hunter and sprints only when necessary to conserve energy.

### 3. Quantitative Evidence (Dashboard)
* **Reward Convergence:** The "Total Reward" graph should show an upward trend, indicating the agent is learning the rules.
* **Efficiency:** The "Steps Taken" metric should decrease for the Hunter (catching faster) and increase for the Survivor (surviving longer).

### 4. Persisted Artifacts
* **Trained Brains:** The system generates `hunter_qtable.pkl` and `survivor_qtable.pkl` files, allowing training to resume across sessions without data loss.

---

##  🛠️ Installation & Run

*** Prerequisites: Python 3.10+ ***

#   Install Dependencies:
    pip install -r requirements.txt
# Run the Game:
    python main.py
# OR use the demo script
    ./run_demo.sh