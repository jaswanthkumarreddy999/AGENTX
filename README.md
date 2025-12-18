# problem Statement 2 : Gamified Learning Environment for AgentX

Build a gamified environment or simulation where AgentX can train, evolve, and demonstrate intelligent behavior.

Examples include:
Puzzle-solving worlds
Resource-optimization challenges
Maze navigation
User-engagement gamification platforms

# Your task:

Design the game mechanics, reward structure, and performance metrics. AgentX should be capable of exploring, learning strategies, and achieving higher scores or faster completion times as training progresses.


# Agent-X: Learning Environment

**Agent-X** is a 2D stealth-action game powered by Reinforcement Learning (Q-Learning). It serves as both a playable game and a Machine Learning simulation environment where autonomous agents learn to hunt players or evade capture through repeated episodes.

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
* **Features:** * No Fog of War.
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

---

## 🧠 AI Architecture

The agents use a **Q-Learning** approach with a lookup table to make decisions based on:
1.  **Distance to Target:** (Euclidean & A* Path distance).
2.  **State:** (Patrolling, Chasing, Evading, Scavenging).
3.  **Memory:** Agents build a "heatmap" of visited locations to encourage exploration.

The "Brains" (`hunter_qtable.pkl` and `survivor_qtable.pkl`) are saved automatically after every match in the `data/brains/` folder.

## 🛠️ Installation & Run

1.  **Requirements:** Python 3.x, Pygame.
2.  **Install Dependencies:**
    ```bash
    pip install pygame
    ```
3.  **Run the Game:**
    ```bash
    python main.py
    ```