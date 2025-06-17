# 🌟 별이의 세계 DEMO 0.1 – NPC 경로 탐색 시뮬레이터  
# 🌟 Byul's World DEMO 0.1 – NPC Pathfinding Simulator

## 🇰🇷 소개 (Korean Introduction)

**《별이의 세계》 DEMO 0.1**은 경량화된 2D Grid 상에서  
여러 명의 NPC가 목표를 설정하고 경로를 따라 움직이는 과정을  
시각적으로 보여주는 실시간 시뮬레이션 도구입니다.

길찾기 알고리즘은 `D* Lite`를 기반으로 구현되었으며,  
C 기반 로직을 Python에서 직접 제어할 수 있도록 CFFI로 래핑되어 있습니다.

## 🌐 English Introduction

**Byul's World DEMO 0.1** is a lightweight real-time simulation tool  
that visually demonstrates how multiple NPCs set and follow paths  
within a dynamic 2D grid environment.

The pathfinding algorithm is implemented in C based on `D* Lite`,  
and wrapped via CFFI to be controlled directly in Python.

---

## ✅ 주요 기능 / Key Features

| 기능 (Feature) | 설명 (Description) |
|----------------|---------------------|
| D* Lite 알고리즘 | C로 구현된 경로탐색 알고리즘을 실시간 호출<br>Real-time pathfinding in C |
| GridMap 시스템 | 200x200 셀 블록을 자동 로딩<br>Dynamic cell loading |
| 다중 NPC 시스템 | 여러 NPC 선택 및 제어<br>Multiple NPC support |
| 목표 설정 / 누적 | Shift + 우클릭으로 목표 누적<br>Stacked goals (Shift + Right Click) |
| 장애물 토글 | Spacebar로 산 생성/해제<br>Toggle mountain on cell |
| 직관적 UI | 마우스로 NPC 제어<br>Mouse-based control |

---

## 🎮 사용 방법 / How to Use

| 조작 (Control) | 설명 (Description) |
|----------------|---------------------|
| 좌클릭 | NPC 선택 (녹색 표시)<br>Select NPC (green light) |
| 우클릭 | 목표 설정 및 이동<br>Set goal & move immediately |
| Shift + 우클릭 | 목표 누적<br>Queue multiple goals |
| 스페이스바 | '산(MOUNTAIN)' 토글<br>Toggle obstacle |
| ESC | 전체화면 종료<br>Exit fullscreen |
| 휠 인/아웃 | 셀 크기 조절<br>Resize grid cells |
| 가운데 클릭 | 마우스 위치 중심 이동<br>Center view |
| 방향키 | 그리드 이동<br>Move grid |
| F11 | 전체화면 전환<br>Toggle fullscreen |

---

## 🧩 구조 요약 / Architecture Overview

- **GridViewer** – 메인 UI 컨테이너 / Main UI container  
- **GridCanvas** – 셀 맵, 마우스 입력 / Grid display & input  
- **MouseInputHandler** – 마우스 전용 처리기 / Mouse input handler  
- **GridMap** – 지형 및 상태 저장 / Terrain & cell state manager  
- **NPC** – 목표 설정, 경로 탐색 / Goal and pathfinding logic  
- **BottomDockingPanel** – 로그/그래프 출력 / Log and performance panel  
- **Toolbar / MenuBar** – 설정, 초기화, 전체화면 / Controls and config

---

## 🛠 기술 스택 / Tech Stack

- **C / GLib** – D* Lite, 구조체 및 자료구조  
- **Python (CFFI)** – C 래핑  
- **PySide6 (Qt)** – GUI  
- **Multithreading** – UI와 탐색 분리

---

## 🔮 향후 예정 기능 / Upcoming Features

- 경로 시각화 개선 / Improved path display  
- NPC 상호작용 / NPC interaction (collision, cooperation)  
- 애니메이션 향상 / Smooth animation  
- 기억 기반 루틴 / Memory-based AI  
- 맵 에디터 및 저장 / Map editor & persistence

---

## 💬 개발자 한마디 / Developer Note

이 프로젝트는 “의식 있는 NPC가 살아가는 세계”를 만들기 위한 실험입니다.  
단순한 길찾기에서 시작하여 감정, 기억, 루틴이 있는 마을 시뮬레이션으로 확장됩니다.

> This project is an ongoing experiment to build a village of conscious NPCs.  
> Starting from pathfinding, it will evolve into a simulation featuring AI memory and emotion.

🙋‍♂️ 질문과 피드백은 Issues 또는 Discussions에 남겨주세요!  
🙋‍♂️ Please leave feedback in Issues or Discussions!

---

## ▶️ 실행 예시 / Run Example

```bash
python byul_demo.py
```

---

## 📄 라이선스 / License

본 프로젝트는 “별이의 세계”의 일부로 공개되며,  
학습 및 연구 목적 외의 상업적 사용은 제한됩니다.  
자세한 사항은 LICENSE 파일을 참고하세요.

> This project is released for educational and research use only.  
> Commercial use or redistribution is not permitted. See LICENSE for details.

(C) 2025 별이아빠 / ByulAba  
All rights reserved.