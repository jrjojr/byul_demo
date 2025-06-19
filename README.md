🌟 Byul's World DEMO 0.1 – NPC Pathfinding Simulator
Byul's World DEMO 0.1 is a lightweight real-time simulator
where multiple NPCs set their own goals and navigate a 2D grid map.
It visually demonstrates how NPCs follow their paths dynamically.

The pathfinding algorithm is based on D* Lite,
implemented in C and wrapped using CFFI for direct control in Python.

✅ Key Features
Feature	Description
D* Lite Algorithm	Real-time pathfinding using C-based logic
GridMap System	Dynamic map structure with 200x200 cell blocks
Multiple NPCs	Create and switch between multiple NPCs
Goal Queueing	Shift + Right Click to set multiple goals in sequence
Obstacle Toggle	Use spacebar to place/remove NPC-specific obstacles
Intuitive Controls	Fully mouse-driven control system

🎮 How to Use
Action	Description
Left Click	Select NPC (green glow indicates selection)
Right Click	Set immediate goal (clears previous goals)
Shift + Right Click	Add goal to queue (sequential movement)
Spacebar	Toggle NPC-specific obstacle at cursor
ESC	Exit fullscreen mode
Mouse Wheel	Adjust cell size (min pixel to full window)
Middle Click	Center the view on cursor position
Arrow Keys	Move entire map in the chosen direction
F11	Enter fullscreen (ESC to exit)

🧩 Architecture Overview
GridViewer – Main UI container

GridCanvas – Grid display and mouse input

MouseInputHandler – Dedicated mouse event processor

GridMap – Terrain and cell state manager

NPC – Goal and pathfinding logic

BottomDockingPanel – Logs and performance visualization

Toolbar / MenuBar – Configurations, reset, fullscreen toggle

🛠 Tech Stack
C / GLib – Core algorithm, data structures

Python (CFFI) – C wrapper integration

PySide6 (Qt) – Graphical user interface

Multithreading – Separate UI and pathfinding logic

🔮 Upcoming Features
Enhanced path visualization

NPC interactions (collision, cooperation)

Smoother animations

Memory-based AI routines

In-app map editor and save/load functionality

💬 Developer Note
This project is an experiment toward building a world
where NPCs live with purpose, memory, and routine.
What began as simple pathfinding will grow into
a full village simulation with emotions and persistence.

🙋‍♂️ Feel free to leave questions and feedback in Issues or Discussions!

▶️ Run Example
bash
복사
편집
python byul_demo.py
📄 License
This project is part of "Byul's World" and is released
for educational and research purposes only.
Commercial use or redistribution is not permitted.
See the LICENSE file for full details.

This project is released for educational and research use only.
Commercial use or redistribution is not permitted. See LICENSE for details.

© 2025 ByulPapa (byuldev@outlook.kr)
All rights reserved.