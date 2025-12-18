# problem Statement 2 : Gamified Learning Environment for AgentX

Build a gamified environment or simulation where AgentX can train, evolve, and demonstrate intelligent behavior.

Examples include:
Puzzle-solving worlds
Resource-optimization challenges
Maze navigation
User-engagement gamification platforms

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

## 🛠️ Installation & Run

1. **Prerequisites:** Python 3.10+
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt