import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: hub
    width: 1280
    height: 860
    minimumWidth: 920
    minimumHeight: 640
    visible: true
    title: "Quant Research Workbench"
    color: "#0d1117"

    readonly property color panel: "#161b22"
    readonly property color border: "#30363d"
    readonly property color textPrimary: "#f0f6fc"
    readonly property color textMuted: "#8b949e"
    readonly property color good: "#3fb950"
    readonly property color warning: "#d29922"

    component EvidenceCard: Rectangle {
        required property string rowLabel
        required property string rowValue
        required property string rowDetail
        required property string rowStatus
        Layout.fillWidth: true
        radius: 8
        color: hub.panel
        border.color: hub.border
        implicitHeight: cardColumn.implicitHeight + 24

        ColumnLayout {
            id: cardColumn
            anchors.fill: parent
            anchors.margins: 12
            spacing: 5
            Label {
                Layout.fillWidth: true
                text: parent.parent.rowLabel
                color: hub.textPrimary
                font.bold: true
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.rowValue
                color: hub.textPrimary
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: text.length > 0
                text: parent.parent.rowDetail
                color: hub.textMuted
                wrapMode: Text.WordWrap
                font.pixelSize: 11
            }
            Label {
                visible: text.length > 0
                text: parent.parent.rowStatus
                color: hub.good
                font.pixelSize: 11
                font.bold: true
            }
        }
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth

        ColumnLayout {
            x: Math.max(24, Math.min(48, parent.width * 0.035))
            y: 30
            width: Math.max(0, parent.width - 2 * x)
            spacing: 18

            Label {
                text: "Quant Research Workbench"
                color: hub.textPrimary
                font.pixelSize: 34
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                text: "UI5 brings the model-comparison story to the center: fit models fairly, freeze them before evaluation, inspect where they fail, and keep model quality separate from parameter identification, hedging evidence, and measured computational cost."
                color: hub.textMuted
                font.pixelSize: 15
                wrapMode: Text.WordWrap
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 12
                color: hub.panel
                border.color: hub.border
                implicitHeight: validationStory.implicitHeight + 36

                ColumnLayout {
                    id: validationStory
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Label {
                        text: "Scientific story"
                        color: hub.textPrimary
                        font.pixelSize: 19
                        font.bold: true
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: hub.width >= 980 ? 3 : 1
                        columnSpacing: 16
                        rowSpacing: 10

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 104
                            radius: 8
                            color: "#0d1117"
                            border.color: hub.border
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                Label {
                                    text: "BLACK-SCHOLES"
                                    color: hub.textPrimary
                                    font.bold: true
                                    font.pixelSize: 17
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "One fitted constant volatility · same training observations"
                                    color: hub.textMuted
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                        Label {
                            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                            text: hub.width >= 980 ? "──────────►\n VALIDATION\n◄──────────" : "▼  VALIDATION  ▼"
                            color: hub.good
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 104
                            radius: 8
                            color: "#0d1117"
                            border.color: hub.border
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                Label {
                                    text: "HESTON"
                                    color: hub.textPrimary
                                    font.bold: true
                                    font.pixelSize: 17
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "Five calibrated coordinates · same training observations"
                                    color: hub.textMuted
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: "M7 evaluates both frozen training fits on the same four held-out contracts. M8 separately measures representative computational workloads. Better pricing, stronger identification, hedging evidence, and faster execution remain different claims."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: hub.width >= 980 ? 2 : 1
                columnSpacing: 14
                rowSpacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    radius: 12
                    color: hub.panel
                    border.color: hub.good
                    implicitHeight: validationCard.implicitHeight + 34
                    ColumnLayout {
                        id: validationCard
                        anchors.fill: parent
                        anchors.margins: 17
                        spacing: 8
                        Label {
                            text: "Validation, Model Risk & Performance"
                            color: hub.textPrimary
                            font.pixelSize: 20
                            font.bold: true
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "Which model fits better? Where? Does the advantage survive a predeclared holdout? Which Heston coordinates are locally fragile? What did M8 actually make faster, and what does its no-C++ decision mean?"
                            color: hub.textPrimary
                            wrapMode: Text.WordWrap
                        }
                        Button {
                            id: validationButton
                            text: "Open Validation Workspace"
                            Accessible.name: "Open validation model risk and performance workspace"
                            onClicked: {
                                hub.hide()
                                validationWindow.show()
                            }
                            KeyNavigation.right: researchButton
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: 12
                    color: hub.panel
                    border.color: hub.border
                    implicitHeight: researchCard.implicitHeight + 34
                    ColumnLayout {
                        id: researchCard
                        anchors.fill: parent
                        anchors.margins: 17
                        spacing: 8
                        Label {
                            text: "Research Workbench Library"
                            color: hub.textPrimary
                            font.pixelSize: 20
                            font.bold: true
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "Open the established UI1–UI4 workflows: Black-Scholes valuation/Greeks, Heston valuation, dynamic hedging, market/IV evidence, and Heston calibration/identifiability."
                            color: hub.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Button {
                            id: researchButton
                            text: "Open Existing Workflows"
                            Accessible.name: "Open existing valuation hedging market and calibration workflows"
                            onClicked: {
                                hub.hide()
                                legacyWorkbench.show()
                            }
                            KeyNavigation.left: validationButton
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 9
                color: "#102318"
                border.color: hub.good
                implicitHeight: m8Label.implicitHeight + 24
                Label {
                    id: m8Label
                    anchors.fill: parent
                    anchors.margins: 12
                    text: "Performance status: M8 is merged. The Workbench presents revision-pinned before/after evidence for the six representative M7 workloads. The four heavy workloads improve by about 4.61×–27.38× in the pinned reference with parity retained. M8's measured native decision is no C++ kernel for v0.1, so UI5 correctly exposes no backend selector. Hosted timings are descriptive evidence, not CI thresholds."
                    color: hub.good
                    wrapMode: Text.WordWrap
                }
            }

            Label {
                Layout.fillWidth: true
                text: "Keyboard: Ctrl+1 opens Validation · Ctrl+2 opens the existing Research Workbench · Ctrl+Q quits. Validation uses Ctrl+R to run, Ctrl+I for the inspector, and Alt+Left to return home."
                color: hub.textMuted
                font.pixelSize: 12
                wrapMode: Text.WordWrap
            }
        }
    }

    UI4Main {
        id: legacyWorkbench
        visible: false
        onClosing: function(close) {
            hub.show()
        }
    }

    ApplicationWindow {
        id: validationWindow
        width: 1480
        height: 920
        minimumWidth: 980
        minimumHeight: 680
        visible: false
        title: "Quant Research Workbench · Validation & Model Risk"
        color: "#0d1117"

        onClosing: function(close) {
            hub.show()
        }

        ValidationWorkspace {
            anchors.fill: parent
            controller: workbenchController
            panelColor: hub.panel
            borderColor: hub.border
            textPrimary: hub.textPrimary
            textMuted: hub.textMuted
            goodColor: hub.good
            warningColor: hub.warning
            onHomeRequested: {
                validationWindow.hide()
                hub.show()
            }
            onInspectorRequested: validationInspector.open()
        }

        Drawer {
            id: validationInspector
            width: Math.min(560, validationWindow.width * 0.46)
            height: validationWindow.height
            edge: Qt.RightEdge
            modal: false
            background: Rectangle {
                color: "#010409"
                border.color: hub.border
            }

            ScrollView {
                anchors.fill: parent
                contentWidth: availableWidth
                ColumnLayout {
                    x: 18
                    y: 18
                    width: Math.max(0, parent.width - 36)
                    spacing: 12
                    Label {
                        text: "Validation Mathematical Inspector"
                        color: hub.textPrimary
                        font.pixelSize: 22
                        font.bold: true
                    }
                    Label {
                        Layout.fillWidth: true
                        text: "Observed quantities, predeclared partition, training fits, validation method, immutable validation evidence, conditioning, and the separate merged-M8 computational evidence remain distinct."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.validationInspectorModel
                        delegate: EvidenceCard {
                            required property string label
                            required property string value
                            required property string detail
                            required property string status
                            rowLabel: label
                            rowValue: value
                            rowDetail: detail
                            rowStatus: status
                        }
                    }
                }
            }
        }
    }

    Shortcut {
        sequence: "Ctrl+1"
        onActivated: {
            hub.hide()
            validationWindow.show()
        }
    }
    Shortcut {
        sequence: "Ctrl+2"
        onActivated: {
            hub.hide()
            legacyWorkbench.show()
        }
    }
    Shortcut {
        sequence: StandardKey.Quit
        onActivated: Qt.quit()
    }
}
