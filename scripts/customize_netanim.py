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
    QPushButton { background: #273449; border: 1px solid #475569; border-radius: 5px; padding: 6px 12px; }
    QPushButton:hover { background: #0f766e; }
    QTableWidget { background: #0b1220; alternate-background-color: #111c2e; gridline-color: #334155; selection-background-color: #0f766e; }
    QHeaderView::section { background: #1e293b; color: #e2e8f0; border: 0; padding: 7px; font-weight: 600; }
    QCheckBox { spacing: 5px; padding: 3px; }
    QSplitter::handle { background: #334155; }
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

# Make the Animator's vertical controls readable instead of showing clipped,
# unlabeled 20-pixel icons.
replace_once(
    SOURCE / "animatorconstants.h",
    "#define VERTICAL_TOOLBAR_WIDTH_DEFAULT 30",
    "#define VERTICAL_TOOLBAR_WIDTH_DEFAULT 124",
)

replace_once(
    SOURCE / "animatormode.cpp",
    '''  m_verticalToolbar->setIconSize (iconSize);
  m_verticalToolbar->setOrientation (Qt::Vertical);''',
    '''  m_verticalToolbar->setIconSize (iconSize);
  m_verticalToolbar->setToolButtonStyle (Qt::ToolButtonTextBesideIcon);
  m_verticalToolbar->setOrientation (Qt::Vertical);''',
)

for path, old, new in [
    ("animatormode.cpp", 'm_stepButton->setToolTip ("Step through the simulation");', 'm_stepButton->setText ("Step");\n  m_stepButton->setToolTip ("Step through the simulation");'),
    ("animatormode.cpp", 'm_zoomInButton->setToolTip ("Zoom in");', 'm_zoomInButton->setText ("Zoom in");\n  m_zoomInButton->setToolTip ("Zoom in");'),
    ("animatormode.cpp", 'm_zoomOutButton->setToolTip ("Zoom out");', 'm_zoomOutButton->setText ("Zoom out");\n  m_zoomOutButton->setToolTip ("Zoom out");'),
    ("animatormode.cpp", 'm_showNodeIdButton->setToolTip ("Show Node Id");', 'm_showNodeIdButton->setText ("Node names");\n  m_showNodeIdButton->setToolTip ("Show Node Id");'),
    ("animatormode.cpp", 'm_showNodeSysIdButton->setToolTip ("Show Node System Id");', 'm_showNodeSysIdButton->setText ("System IDs");\n  m_showNodeSysIdButton->setToolTip ("Show Node System Id");'),
    ("animatormode.cpp", 'm_showWirelessCirclesButton->setToolTip ("Toggle Show Wireless Circles Animation");', 'm_showWirelessCirclesButton->setText ("Radio waves");\n  m_showWirelessCirclesButton->setToolTip ("Toggle Show Wireless Circles Animation");'),
    ("animatormode.cpp", 'm_blockPacketsButton->setToolTip ("Show packets");', 'm_blockPacketsButton->setText ("Packets");\n  m_blockPacketsButton->setToolTip ("Show packets");'),
    ("animatormode.cpp", 'm_resetButton->setText ("R");', 'm_resetButton->setText ("Replay");'),
    ("animatormode.cpp", 'm_showMetaButton->setText ("M");', 'm_showMetaButton->setText ("Packet info");'),
    ("animatormode.cpp", 'm_showPropertiesButton->setText ("Pr");', 'm_showPropertiesButton->setText ("Details");'),
]:
    replace_once(SOURCE / path, old, new)

# Use a readable packet timeline: light node lanes, teal arrows, no repeated
# black packet labels, and data packets instead of neighbour-discovery traffic.
replace_once(
    SOURCE / "packetsscene.cpp",
    '''  m_textBubble = new TextBubble ("Info:", "No data available\\nDid you load the XML file?");''',
    '''  setBackgroundBrush (QColor ("#0b1220"));
  m_textBubble = new TextBubble ("Info:", "No data available\\nDid you load the XML file?");''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    '''      QGraphicsLineItem * lineItem = addLine (m_interNodeSpacing * lineIndex, m_borderHeight, m_interNodeSpacing * lineIndex, m_lineLength);
      m_nodeLines[m_allowedNodes[lineIndex]] = lineItem;''',
    '''      QGraphicsLineItem * lineItem = addLine (m_interNodeSpacing * lineIndex, m_borderHeight, m_interNodeSpacing * lineIndex, m_lineLength);
      lineItem->setPen (QPen (QColor ("#475569"), 2));
      m_nodeLines[m_allowedNodes[lineIndex]] = lineItem;''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    '''      m_nodeIdTexts.push_back (nodeIdText);
      nodeIdText->setPos''',
    '''      m_nodeIdTexts.push_back (nodeIdText);
      nodeIdText->setBrush (QColor ("#f8fafc"));
      QFont nodeFont = nodeIdText->font ();
      nodeFont.setBold (true);
      nodeFont.setPointSize (11);
      nodeIdText->setFont (nodeFont);
      nodeIdText->setPos''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    '''  m_rulerLine->setLine (RULER_X, m_borderHeight, RULER_X, m_lineLength);
  return foundNodes;''',
    '''  m_rulerLine->setLine (RULER_X, m_borderHeight, RULER_X, m_lineLength);
  m_rulerLine->setPen (QPen (QColor ("#64748b"), 2));
  return foundNodes;''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    '''      m_packetLines.push_back (graphPacket);
      QGraphicsSimpleTextItem * info = new QGraphicsSimpleTextItem (shortMeta);
      addItem (info);
      m_packetInfoTexts.push_back (info);
      info->setFlag (QGraphicsItem::ItemIgnoresTransformations);
      info->setPos (QPointF (fromNodeX, txY));
      qreal textAngle = graphPacket->line().angle ();
      if(textAngle < 90)
        {
          textAngle = 360-textAngle;
        }
      else if (textAngle > 270)
        {
          textAngle = 360-textAngle;
        }
      else
        {
          textAngle = 180-textAngle;
          info->setPos (QPointF (toNodeX, rxY));

        }
      info->setTransform (QTransform ().rotate (textAngle));''',
    '''      m_packetLines.push_back (graphPacket);''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    '''  m_packetPathItem = new QGraphicsPathItem;
  addItem (m_packetPathItem);
  m_packetPath = QPainterPath ();''',
    '''  m_packetPathItem = new QGraphicsPathItem;
  m_packetPathItem->setPen (QPen (QColor ("#22d3ee"), 2));
  addItem (m_packetPathItem);
  m_packetPath = QPainterPath ();''',
)

replace_once(
    SOURCE / "packetsscene.cpp",
    'm_filterRegex (".*"),',
    'm_filterRegex ("expires_ns=[1-9]"),',
)

replace_once(
    SOURCE / "packetsmode.cpp",
    'm_regexFilterEdit = new QLineEdit (".*");',
    'm_regexFilterEdit = new QLineEdit ("expires_ns=[1-9]");',
)

replace_once(
    SOURCE / "packetsmode.cpp",
    '''      qreal thousandthPacketTime = AnimatorMode::getInstance ()->getThousandthPacketTime ();
      if (thousandthPacketTime < 0)
        m_toTime = lastPacketTime;
      else
        m_toTime = thousandthPacketTime;
      m_fromTime = AnimatorMode::getInstance ()->getFirstPacketTime ();''',
    '''      m_toTime = lastPacketTime;
      m_fromTime = AnimatorMode::getInstance ()->getFirstPacketTime ();''',
)

replace_once(
    SOURCE / "table.cpp",
    '#include "table.h"',
    '#include "table.h"\n#include <QHeaderView>',
)

replace_once(
    SOURCE / "table.cpp",
    '''  m_table = new QTableWidget;
  m_vLayout = new QVBoxLayout;''',
    '''  m_table = new QTableWidget;
  m_table->setAlternatingRowColors (true);
  m_table->setSelectionBehavior (QAbstractItemView::SelectRows);
  m_table->verticalHeader ()->setDefaultSectionSize (26);
  m_vLayout = new QVBoxLayout;''',
)

# NetAnim 3.110 reads compact NS-3 <pr>/<wpr> packet references but stops before
# turning each wireless reception into a playback event. Continue into the
# normal wireless-packet case so the trace actually animates.
replace_once(
    SOURCE / "animxmlparser.cpp",
    '''          parsedElement.meta_info = ref.meta_info;
          break;
        }
        case XML_WPACKET_RX:''',
    '''          parsedElement.meta_info = ref.meta_info;
          // A compact wpr element is now a complete wireless packet event.
        }
        [[fallthrough]];
        case XML_WPACKET_RX:''',
)

replace_once(
    SOURCE / "animxmlparser.cpp",
    '''  parsedElement.packetrx_lbRx = m_reader->attributes ().value ("lbRx").toString ().toDouble ();
  setMaxSimulationTime (parsedElement.packetrx_lbRx);
  return parsedElement;
}


ParsedElement
Animxmlparser::parseNode ()''',
    '''  parsedElement.packetrx_lbRx = m_reader->attributes ().value ("lbRx").toString ().toDouble ();
  if (!parsedElement.packetrx_lbRx && parsedElement.packetrx_fbRx)
    {
      parsedElement.packetrx_lbRx = parsedElement.packetrx_fbRx;
    }
  setMaxSimulationTime (parsedElement.packetrx_lbRx);
  return parsedElement;
}


ParsedElement
Animxmlparser::parseNode ()''',
)

# Keep replay controls usable after the last event. Upstream disables Play and
# continuously restarts a decorative animation on the Reload button.
replace_once(
    SOURCE / "animatormode.cpp",
    '''  m_updateRateTimer->stop ();
  m_playButton->setEnabled (false);
  m_simulationTimeSlider->setEnabled (false);
  QApplication::processEvents ();
  //clickResetSlot ();
  m_events.rewind ();
  //setCurrentTime (0);
  m_simulationTimeSlider->setEnabled (false);
  //NS_LOG_DEBUG ("Simulation Completed");
  m_bottomStatusLabel->setText ("Simulation Completed");

  m_buttonAnimationGroup = new QParallelAnimationGroup;
  //m_buttonAnimationGroup->addAnimation (getButtonAnimation (m_fileOpenButton));
  m_buttonAnimationGroup->addAnimation (getButtonAnimation (m_reloadFileButton));

  m_buttonAnimationGroup->start ();

  connect(m_buttonAnimationGroup,
          &QParallelAnimationGroup::finished,
          this,
          &AnimatorMode::buttonAnimationGroupFinishedSlot);''',
    '''  m_updateRateTimer->stop ();
  m_playing = false;
  m_playButton->setIcon (QIcon (":/resources/animator_play.svg"));
  m_playButton->setToolTip ("Replay Animation");
  m_playButton->setEnabled (true);
  m_simulationTimeSlider->setEnabled (true);
  m_events.rewind ();
  m_bottomStatusLabel->setText ("Simulation completed — press Play to replay");''',
)

# Add a small public entry point so the launcher can load and play the exact XML
# passed on the command line instead of requiring the file dialog.
replace_once(
    SOURCE / "animatormode.h",
    '''  void start ();
  void openPropertyBroswer ();''',
    '''  void start ();
  void openPropertyBroswer ();
  bool loadTraceFile (QString traceFileName, bool autoPlay);''',
)

replace_once(
    SOURCE / "animatormode.cpp",
    '''bool
AnimatorMode::parseXMLTraceFile (QString traceFileName)
{''',
    '''bool
AnimatorMode::loadTraceFile (QString traceFileName, bool autoPlay)
{
  StatsMode::getInstance ()->systemReset ();
  systemReset ();
  m_traceFileName = traceFileName;
  bool loaded = parseXMLTraceFile (traceFileName);
  StatsMode::getInstance ()->systemReset ();
  QApplication::processEvents ();
  if (loaded)
    {
      clickResetSlot ();
      m_updateRateSlider->setValue (17);
      qInfo () << "Loaded" << traceFileName << "with" << m_events.getCount ()
               << "playback events";
      if (autoPlay)
        {
          clickPlaySlot ();
        }
    }
  return loaded;
}

bool
AnimatorMode::parseXMLTraceFile (QString traceFileName)
{''',
)

replace_once(
    SOURCE / "main.cpp",
    '#include "netanim.h"',
    '#include "netanim.h"\n#include "animatormode.h"',
)

replace_once(
    SOURCE / "main.cpp",
    '''  netanim::NetAnim netAnim;
  return app.exec ();''',
    '''  netanim::NetAnim netAnim;
  if (argc > 1)
    {
      QString traceFile = QString::fromLocal8Bit (argv[1]);
      QTimer::singleShot (0, [traceFile] () {
        netanim::AnimatorMode::getInstance ()->loadTraceFile (traceFile, true);
      });
    }
  return app.exec ();''',
)

print("Applied Deadline Routing NetAnim theme")
