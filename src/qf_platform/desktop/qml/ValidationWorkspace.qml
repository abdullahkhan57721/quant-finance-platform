import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    required property var controller
    required property color panelColor
    required property color borderColor
    required property color textPrimary
    required property color textMuted
    required property color goodColor
    required property color warningColor

    signal homeRequested()
    signal inspectorRequested()

    component EvidenceCard: Rectangle {
        required property string rowLabel
        required property string rowValue
        required property string rowDetail
        required property string rowStatus
        Layout.fillWidth: true
        radius: 8
        color: root.panelColor
        border.color: root.borderColor
        implicitHeight: content.implicitHeight + 24
        Accessible.name: rowLabel + ": " + rowValue

        ColumnLayout {
            id: content
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 12
            spacing: 5
            Label {
                Layout.fillWidth: true
                text: parent.parent.rowLabel
                color: root.textPrimary
                font.bold: true
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.rowValue
                color: root.textPrimary
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: text.length > 0
                text: parent.parent.rowDetail
                color: root.textMuted
                wrapMode: Text.WordWrap
                font.pixelSize: 11
            }
            Label {
                visible: text.length > 0
                text: parent.parent.rowStatus
                color: rowStatus === "Unsupported" ? root.warningColor : root.goodColor
                font.pixelSize: 11
                font.bold: true
            }
        }
    }

    component EvidenceList: ColumnLayout {
        required property var sourceModel
        Layout.fillWidth: true
        spacing: 8
        Repeater {
            model: parent.sourceModel
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

    Rectangle { anchors.fill: parent; color: "#0d1117" }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(14, Math.min(26, root.width * 0.02))
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Button {
                id: homeButton
                text: "← Home"
                Accessible.name: "Return to Workbench home"
                onClicked: root.homeRequested()
                KeyNavigation.right: runButton
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Label {
                    text: "Validation & Model Risk"
                    color: root.textPrimary
                    font.pixelSize: 26
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Black-Scholes and Heston are fitted on the same TRAIN partition, frozen, then evaluated on the same held-out contracts. Better fit, parameter identification, hedging evidence, and measured computational cost remain different questions."
                    color: root.textMuted
                    wrapMode: Text.WordWrap
                }
            }
            Button {
                id: inspectorButton
                text: "Mathematics Inspector"
                Accessible.name: "Open validation mathematics inspector"
                onClicked: root.inspectorRequested()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Button {
                id: runButton
                text: controller.running ? "Validation running…" : "Run M7 Validation"
                enabled: !controller.running
                Accessible.name: "Run M7 Black-Scholes versus Heston validation"
                onClicked: controller.runValidationStudy()
                KeyNavigation.left: homeButton
                KeyNavigation.right: inspectorButton
            }
            Label {
                Layout.fillWidth: true
                text: controller.status
                color: controller.running ? root.warningColor : root.textMuted
                wrapMode: Text.WordWrap
            }
        }

        Rectangle {
            Layout.fillWidth: true
            visible: controller.running
            radius: 8
            color: "#1f1608"
            border.color: root.warningColor
            implicitHeight: runningLabel.implicitHeight + 20
            Label {
                id: runningLabel
                anchors.fill: parent
                anchors.margins: 10
                text: "Long-running operation: the production M7 API exposes no progress stream or cancellation contract, so UI5 shows truthful busy state only. Results appear only after the immutable validation evidence is complete."
                color: root.warningColor
                wrapMode: Text.WordWrap
            }
        }

        Rectangle {
            Layout.fillWidth: true
            visible: !controller.validationAnalysisReady && !controller.running && tabs.currentIndex !== 4
            radius: 10
            color: root.panelColor
            border.color: root.borderColor
            implicitHeight: emptyColumn.implicitHeight + 32
            ColumnLayout {
                id: emptyColumn
                anchors.fill: parent
                anchors.margins: 16
                Label {
                    text: "No validation evidence loaded yet"
                    color: root.textPrimary
                    font.pixelSize: 18
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Run the deterministic M7 reference study for pricing/model-risk evidence, or open Performance now to inspect the already-committed M8 before/after measurements and native decision."
                    color: root.textMuted
                    wrapMode: Text.WordWrap
                }
            }
        }

        TabBar {
            id: tabs
            Layout.fillWidth: true
            currentIndex: 0
            focus: true
            Accessible.name: "Validation evidence sections"
            TabButton { text: "Overview" }
            TabButton { text: "Residuals" }
            TabButton { text: "Stability" }
            TabButton { text: "Model Risk" }
            TabButton { text: "Performance" }
            TabButton { text: "Report" }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: controller.validationAnalysisReady || tabs.currentIndex === 4
            currentIndex: tabs.currentIndex

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 12
                    EvidenceList { sourceModel: controller.validationSummaryModel }
                    GridLayout {
                        Layout.fillWidth: true
                        columns: root.width >= 1120 ? 2 : 1
                        columnSpacing: 12
                        rowSpacing: 12
                        Rectangle {
                            Layout.fillWidth: true
                            color: "transparent"
                            implicitHeight: trainColumn.implicitHeight
                            ColumnLayout {
                                id: trainColumn
                                width: parent.width
                                Label { text: "TRAINING"; color: root.textPrimary; font.bold: true; font.pixelSize: 16 }
                                EvidenceList { sourceModel: controller.validationTrainingMetricModel }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            color: "transparent"
                            implicitHeight: evalColumn.implicitHeight
                            ColumnLayout {
                                id: evalColumn
                                width: parent.width
                                Label { text: "HELD-OUT EVALUATION"; color: root.textPrimary; font.bold: true; font.pixelSize: 16 }
                                EvidenceList { sourceModel: controller.validationEvaluationMetricModel }
                            }
                        }
                    }
                    PlotCanvas {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 380
                        plotJson: controller.validationHeldOutErrorPlotJson
                    }
                }
            }

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 12
                    PlotCanvas {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 420
                        plotJson: controller.validationResidualPlotJson
                    }
                    Label {
                        Layout.fillWidth: true
                        text: "Contract-level evidence"
                        color: root.textPrimary
                        font.bold: true
                        font.pixelSize: 17
                    }
                    EvidenceList { sourceModel: controller.validationResidualModel }
                }
            }

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 12
                    PlotCanvas {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 390
                        plotJson: controller.validationParameterStabilityPlotJson
                    }
                    EvidenceList { sourceModel: controller.validationStabilityModel }
                }
            }

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 12
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 8
                        color: "#1f1608"
                        border.color: root.warningColor
                        implicitHeight: riskBoundary.implicitHeight + 24
                        Label {
                            id: riskBoundary
                            anchors.fill: parent
                            anchors.margins: 12
                            text: "Heston's held-out pricing advantage is real M7 evidence. It is not evidence of temporal forecasting, universal model validity, or superior Heston hedging. M3 remains a Black-Scholes/GBM hedge experiment until a Heston path + Delta + hedge-accounting backend exists."
                            color: root.warningColor
                            wrapMode: Text.WordWrap
                        }
                    }
                    EvidenceList { sourceModel: controller.validationRiskModel }
                }
            }

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 12
                    Label {
                        Layout.fillWidth: true
                        text: "Merged M8 measured the predeclared M7 workloads on the same hosted runner before and after Python/NumPy optimization. Hosted timings are descriptive evidence, not CI thresholds. The scalar reference workloads were intentionally not optimized."
                        color: root.textMuted
                        wrapMode: Text.WordWrap
                    }
                    PlotCanvas {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 390
                        plotJson: controller.performanceRuntimePlotJson
                    }
                    Label { text: "Representative workloads"; color: root.textPrimary; font.bold: true; font.pixelSize: 17 }
                    EvidenceList { sourceModel: controller.performanceWorkloadModel }
                    Label { text: "Correctness / parity"; color: root.textPrimary; font.bold: true; font.pixelSize: 17 }
                    EvidenceList { sourceModel: controller.performanceParityModel }
                    Label { text: "Native acceleration decision"; color: root.textPrimary; font.bold: true; font.pixelSize: 17 }
                    EvidenceList { sourceModel: controller.performanceNativeDecisionModel }
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 8
                        color: "#102318"
                        border.color: root.goodColor
                        implicitHeight: nativeBoundary.implicitHeight + 24
                        Label {
                            id: nativeBoundary
                            anchors.fill: parent
                            anchors.margins: 12
                            text: "M8's measured conclusion is not 'C++ failed' or 'C++ is never useful.' The heavy v0.1 workloads became fast enough in Python/NumPy that the compiler, binding, packaging, and extra parity surface is not currently justified. Larger future workloads must profile again."
                            color: root.goodColor
                            wrapMode: Text.WordWrap
                        }
                    }
                    Label { text: "Evidence provenance"; color: root.textPrimary; font.bold: true; font.pixelSize: 17 }
                    EvidenceList { sourceModel: controller.performanceProvenanceModel }
                }
            }

            ScrollView {
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width
                    spacing: 10
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            Layout.fillWidth: true
                            text: "Evidence report"
                            color: root.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }
                        Button {
                            text: "Copy Evidence Report"
                            Accessible.name: "Copy UI5 validation and performance evidence report to clipboard"
                            onClicked: {
                                reportArea.selectAll()
                                reportArea.copy()
                                reportArea.deselect()
                            }
                        }
                    }
                    Label {
                        Layout.fillWidth: true
                        text: "This concrete export surface combines already-owned M7 validation evidence with the committed M8 performance reference. UI5 does not introduce a generic report generator, arbitrary file-export framework, or project persistence model."
                        color: root.textMuted
                        wrapMode: Text.WordWrap
                    }
                    TextArea {
                        id: reportArea
                        Layout.fillWidth: true
                        Layout.preferredHeight: 520
                        readOnly: true
                        selectByMouse: true
                        wrapMode: TextEdit.Wrap
                        text: controller.ui5EvidenceReportText
                        color: root.textPrimary
                        selectionColor: "#264f78"
                        selectedTextColor: "#ffffff"
                        background: Rectangle { color: root.panelColor; border.color: root.borderColor; radius: 8 }
                        Accessible.name: "UI5 validation and performance evidence report text"
                    }
                }
            }
        }
    }

    Shortcut { sequence: "Ctrl+R"; enabled: !controller.running; onActivated: controller.runValidationStudy() }
    Shortcut { sequence: "Ctrl+I"; onActivated: root.inspectorRequested() }
    Shortcut { sequence: "Alt+Left"; onActivated: root.homeRequested() }
}
