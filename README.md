# 🌟 Byul's World DEMO 0.1 – NPC Pathfinding Simulator

**Byul's World DEMO 0.1** is a lightweight real-time simulator
where multiple NPCs set their own goals and navigate a 2D grid map.
It visually demonstrates how NPCs follow their paths dynamically.

The pathfinding algorithm is based on `D* Lite`,
implemented in C and wrapped using CFFI for direct control in Python.

> 💖 If you find this project interesting or helpful, you can support its development here: [paypal.me/jrjojr](https://paypal.me/jrjojr)

---

## ✅ Key Features

| Feature            | Description                                           |
| ------------------ | ----------------------------------------------------- |
| D\* Lite Algorithm | Real-time pathfinding using C-based logic             |
| GridMap System     | Dynamic map structure with 200x200 cell blocks        |
| Multiple NPCs      | Create and switch between multiple NPCs               |
| Goal Queueing      | Shift + Right Click to set multiple goals in sequence |
| Obstacle Toggle    | Spacebar toggles NPC-specific obstacles at cursor     |
| Intuitive Controls | Fully mouse-driven control system                     |

---

## 🎮 How to Use

| Action              | Description                                 |
| ------------------- | ------------------------------------------- |
| Left Click          | Select NPC (green glow indicates selection) |
| Right Click         | Set immediate goal (clears previous goals)  |
| Shift + Right Click | Add goal to queue (sequential movement)     |
| Spacebar            | Toggle NPC-specific obstacle at cursor      |
| ESC                 | Exit fullscreen mode                        |
| Mouse Wheel         | Adjust cell size (min pixel to full window) |
| Middle Click        | Center view on mouse position               |
| Arrow Keys          | Move the entire map                         |
| F11                 | Enter fullscreen (use ESC to exit)          |

---

## 🧩 Architecture Overview

* **GridViewer** – Main UI container
* **GridCanvas** – Grid display and mouse input
* **MouseInputHandler** – Dedicated mouse event processor
* **GridMap** – Terrain and cell state manager
* **NPC** – Goal and pathfinding logic
* **BottomDockingPanel** – Logs and performance visualization
* **Toolbar / MenuBar** – Configuration, reset, fullscreen toggle

---

## 🛠 Tech Stack

* **C / GLib** – Core algorithm, data structures
* **Python (CFFI)** – C wrapper integration
* **PySide6 (Qt)** – GUI framework
* **Multithreading** – Separate UI and pathfinding logic

---

## 🔮 Upcoming Features

* Enhanced path visualization
* NPC interaction (collision, cooperation)
* Smoother animations
* Memory-based AI routines
* Map editor and persistence

---

## 💬 Developer Note

This project is an experiment to create a world
where NPCs live with purpose, memory, and routine.
What started as a simple pathfinding simulator
will grow into a living village simulation.

🙋‍♂️ Feel free to leave feedback or questions via Issues or Discussions!

---

## ▶️ Run Example

```bash
python byul_demo.py
```

---

## 📄 License

This project is part of "Byul's World"
and is released for **educational and research use only**.
**Commercial use or redistribution is not permitted.**
See the LICENSE file for full details.

© 2025 ByulPapa ([byuldev@outlook.kr](mailto:byuldev@outlook.kr))
All rights reserved.
