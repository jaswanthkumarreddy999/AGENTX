# 🐛 Known Bugs & 🚀 Feature Requests

## 🔴 Critical Bugs (Priority High)

### 1. AI Targeting Error: Wall Hugging (Coordinate Glitch)
* **Status:** ❌ Open
* **Description:** When a target (Player or AI) is moving extremely close to a wall ("hugging" the wall), their float coordinates (e.g., `x=5.9`, `y=10.0`) might round up to the wall's tile coordinate (e.g., `x=6`).
* **Symptom:** The AI Hunter stops moving or gets stuck because its pathfinding algorithm (A*) calculates that the target is *inside* a wall node, making it unreachable.
* **Proposed Fix:** * Modify `AgentX.update()` or the pathfinding call.
    * **Center of Mass Check:** Instead of using raw `int(x)`, use `int(x + 0.5)` specifically for rendering, but for targeting, check the tile density.
    * **Fallback Logic:** If `map.is_wall(target_x, target_y)` is True, the AI must target the **nearest walkable neighbor** of the target, rather than the target itself.

### 2. Agent Stuck Collision
* **Status:** ⚠️ Partial Fix Applied (Smart Evasion added)
* **Description:** Agents occasionally vibrate when touching walls during evasion.
* **Note:** Keep monitoring this in high-speed training mode.

---

## 🟡 Visual / UI Bugs (Priority Medium)

### 1. Dashboard Metric Mismatch (Resolved)
* **Status:** ✅ Fixed
* **Previous Issue:** Dashboard was showing AI XP for human players.
* **Fix:** Added logic to detect `agent_role` and display "PLAYER RANK: HUMAN" instead of neural stats.

---

## 🚀 Feature Wishlist

### 1. Manual Brain Management
* **Idea:** Add a button in the dashboard or a command-line argument to "Reset Brains" or "Load Specific Brain Checkpoint" (e.g., `load brain_v1.pkl`).

### 2. Map Editor / Random Seeds
* **Idea:** Allow the player to enter a seed for the `MazeGenerator` to replay specific map layouts.

### 3. Visual Scent Trail
* **Idea:** For the Hunter AI, render a faint "scent trail" showing where the Survivor was 5 seconds ago, to visualize the AI's tracking logic.