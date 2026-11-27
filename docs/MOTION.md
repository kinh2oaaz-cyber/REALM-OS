# Motion engine

**Important honesty note:** The user asked for *Framer Motion*. **Framer
Motion is a React/JavaScript library** and cannot run inside REALM OS,
which is **PySide6/Python** (no React, no browser DOM). We did **not**
fake it.

Instead REALM OS uses **Qt's own animation engine** (`ui/motion.py`):

- `QPropertyAnimation`, `QEasingCurve`, `QVariantAnimation`,
  `QSequentialAnimationGroup`, `QGraphicsOpacityEffect`,
  `QGraphicsBlurEffect`, `QTimer`.
- `fade_in`, `fade_out`, `slide_in`, `pop`, `page_transition`,
  `smooth_scroll`.
- **Page transitions** on navigation (`MainWindow.navigate` →
  `page_transition`), fade + slide, `OutCubic`.
- **Frosted-glass blur** (`ui/background.py`): pre-blurred red+gold
  background + `QGraphicsBlurEffect`.
- Respects `appearance.reduce_motion`.

QSS `:hover`/`:pressed` transitions plus these animations provide
smooth, premium motion without any extra dependency or JavaScript.

**Alternatives considered (honest):**
- QML/Qt Quick has its own animation engine (`Behavior`, `NumberAnimation`,
  `Transition`, `SequentialAnimation`) — still **not** Framer Motion.
- `QtWebEngine` + a React app + Framer Motion — would be real Framer
  Motion but a full UI re-architecture; not done.
