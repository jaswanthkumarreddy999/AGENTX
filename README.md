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
##  🛠️ Installation & Run

*** Prerequisites: Python 3.10+ ***

#   Install Dependencies:
    pip install -r requirements.txt
# Run the Game:
    python main.py