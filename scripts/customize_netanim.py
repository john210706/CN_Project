#!/usr/bin/env python3
"""Apply the project's small, repeatable visual theme to NetAnim."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "vendor/netanim-3.110/src"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Cannot theme {path}: expected source text was not found")
    path.write_text(text.replace(old, new, 1))


replace_once(
    SOURCE / "main.cpp",
    "  QApplication app (argc, argv);\n  app.setApplicationName (\"NetAnim\");",
    '''  QApplication app (argc, argv);
  app.setStyle ("Fusion");
  app.setStyleSheet (R"(
    QWidget { background: #111827; color: #e5e7eb; font-size: 13px; }
    QTabWidget::pane { border: 1px solid #334155; border-radius: 6px; }
    QTabBar::tab { background: #1f2937; padding: 9px 18px; margin-right: 2px; }
    QTabBar::tab:selected { background: #0f766e; color: white; }
    QToolBar { background: #172033; border: 0; spacing: 6px; padding: 6px; }
    QToolButton { background: #273449; border: 1px solid #3b4b63; border-radius: 5px; padding: 5px; }
    QToolButton:hover { background: #0f766e; }
    QComboBox, QSpinBox, QLineEdit { background: #0f172a; border: 1px solid #475569; border-radius: 5px; padding: 5px; }
    QGraphicsView { background: #0b1220; border: 1px solid #334155; border-radius: 6px; }
    QProgressBar { background: #0f172a; border: 1px solid #334155; border-radius: 4px; }
    QProgressBar::chunk { background: #14b8a6; }
  )");
  app.setApplicationName ("Deadline Routing Visualizer");''',
)

replace_once(
    SOURCE / "animatormode.cpp",
    'QString labelStyleSheet = "QLabel {color: black; font: 10px}";',
    'QString labelStyleSheet = "QLabel {color: #cbd5e1; font-size: 12px; font-weight: 600}";',
)

replace_once(
    SOURCE / "animnode.cpp",
    "  m_nodeDescription = new QGraphicsTextItem (nodeDescription);\n  m_nodeDescription->setFlag",
    '''  m_nodeDescription = new QGraphicsTextItem (nodeDescription);
  m_nodeDescription->setDefaultTextColor (QColor ("#e5e7eb"));
  QFont labelFont = m_nodeDescription->font ();
  labelFont.setPointSize (11);
  labelFont.setWeight (QFont::DemiBold);
  m_nodeDescription->setFont (labelFont);
  m_nodeDescription->setFlag''',
)

replace_once(
    SOURCE / "animatorscene.cpp",
    "  m_mousePositionLabel = new QLabel (\"\");",
    '''  setBackgroundBrush (QColor ("#0b1220"));
  m_mousePositionLabel = new QLabel ("");''',
)

replace_once(
    SOURCE / "animatorscene.cpp",
    "      item->setFlag (QGraphicsItem::ItemIgnoresTransformations);",
    '''      item->setFlag (QGraphicsItem::ItemIgnoresTransformations);
      item->setBrush (QColor ("#64748b"));''',
)

print("Applied Deadline Routing NetAnim theme")
