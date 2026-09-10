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

    function invalidate() {
        controller.invalidateUi4Result("calibration")
    }

    component EvidenceCard: Rectangle {
        required property string rowLabel
        required property string rowValue
        required property string rowDetail
        required property string rowStatus
        Layout.fillWidth: true
        radius: 8
        color: root.panelColor
        border.color: root.borderColor
        implicitHeight: contentColumn.implicitHeight + 22

        ColumnLayout {
            id: contentColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 11
            spacing: 4
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
                font.pixelSize: 11
                wrapMode: Text.WordWrap
            }
            Label {
                visible: text.length > 0
                text: parent.parent.rowStatus
                color: root.goodColor
                font.pixelSize: 11
                font.bold: true
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#0d1117"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "← Home"
                onClicked: root.homeRequested()
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Label {
                    text: "Heston Calibration / Inverse Problem"
                    color: root.textPrimary
                    font.pixelSize: 26
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Targets + Heston forward operator + weighting/bounds define the calibration problem. The optimizer is a separate numerical method; convergence and parameter identification remain separate claims."
                    color: root.textMuted
                    wrapMode: Text.WordWrap
                }
            }
            Button {
                text: "Mathematics Inspector"
                visible: modeTabs.currentIndex < 2
                enabled: controller.calibrationAnalysisReady
                onClicked: root.inspectorRequested()
            }
        }

        Label {
            Layout.fillWidth: true
            text: controller.status
            color: controller.running ? root.warningColor : root.textMuted
            wrapMode: Text.WordWrap
        }

        TabBar {
            id: modeTabs
            Layout.fillWidth: true
            TabButton { text: "Synthetic truth recovery" }
            TabButton { text: "Thin identifiability counterexample" }
            TabButton { text: "M6 SPX reference" }
            onCurrentIndexChanged: {
                if (currentIndex < 2)
                    root.invalidate()
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: modeTabs.currentIndex

            Item {
                id: recoveryPage
                RowLayout {
                    anchors.fill: parent
                    spacing: 14

                    Rectangle {
                        Layout.preferredWidth: 350
                        Layout.fillHeight: true
                        radius: 10
                        color: root.panelColor
                        border.color: root.borderColor

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 14
                            contentWidth: availableWidth

                            ColumnLayout {
                                width: parent.width
                                spacing: 9
                                Label {
                                    text: "Known-truth experiment"
                                    color: root.textPrimary
                                    font.pixelSize: 18
                                    font.bold: true
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "M6 reference truth: v₀=0.04, κ=2, θ=0.04, ξ=0.5, ρ=-0.7. Twenty synthetic call prices span four maturities × five strikes. Change only the optimizer's initial guess below."
                                    color: root.textMuted
                                    wrapMode: Text.WordWrap
                                }

                                Label { text: "Initial v₀"; color: root.textPrimary }
                                TextField {
                                    id: recoveryV0
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationInitialVariance
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial κ"; color: root.textPrimary }
                                TextField {
                                    id: recoveryKappa
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationKappa
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial θ"; color: root.textPrimary }
                                TextField {
                                    id: recoveryTheta
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationTheta
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial ξ"; color: root.textPrimary }
                                TextField {
                                    id: recoveryXi
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationXi
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial ρ"; color: root.textPrimary }
                                TextField {
                                    id: recoveryRho
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationRho
                                    onTextEdited: root.invalidate()
                                }

                                CheckBox {
                                    id: recoveryAdvanced
                                    text: "Advanced optimizer/numerical settings"
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    visible: recoveryAdvanced.checked
                                    Label { text: "Max function evaluations"; color: root.textPrimary }
                                    TextField {
                                        id: recoveryMaxEval
                                        Layout.fillWidth: true
                                        text: controller.defaultCalibrationMaxEvaluations
                                        onTextEdited: root.invalidate()
                                    }
                                    Label { text: "Heston Fourier intervals"; color: root.textPrimary }
                                    TextField {
                                        id: recoveryIntervals
                                        Layout.fillWidth: true
                                        text: controller.defaultCalibrationFourierIntervals
                                        onTextEdited: root.invalidate()
                                    }
                                    Label {
                                        Layout.fillWidth: true
                                        text: "Target space is option price with uniform residual scale. Financial bounds are fixed to the M6 deterministic recovery domain. Feller is diagnostic, not an enforced constraint."
                                        color: root.textMuted
                                        font.pixelSize: 11
                                        wrapMode: Text.WordWrap
                                    }
                                }

                                Button {
                                    Layout.fillWidth: true
                                    text: controller.running ? "Calibration running…" : "Run truth recovery"
                                    enabled: !controller.running
                                    onClicked: controller.runHestonCalibration(
                                        "recovery",
                                        recoveryV0.text,
                                        recoveryKappa.text,
                                        recoveryTheta.text,
                                        recoveryXi.text,
                                        recoveryRho.text,
                                        recoveryAdvanced.checked ? recoveryMaxEval.text : controller.defaultCalibrationMaxEvaluations,
                                        recoveryAdvanced.checked ? recoveryIntervals.text : controller.defaultCalibrationFourierIntervals
                                    )
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "No progress percentage is shown: merged M6 exposes no optimizer progress stream."
                                    color: root.textMuted
                                    font.pixelSize: 11
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        contentWidth: availableWidth
                        ColumnLayout {
                            width: parent.width
                            spacing: 12

                            Label { text: "Calibration problem"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationProblemModel
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

                            Label { text: "Known truth"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationTruthModel
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

                            Label { text: "Multiple starts"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationRunModel
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

                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationParameterErrorPlotJson }
                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationObjectivePlotJson }
                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationResidualPlotJson }

                            Label { text: "Conditioning & interpretation"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationConditioningModel
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

                            Label { text: "Per-target residuals"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationResidualModel
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

            Item {
                id: thinPage
                RowLayout {
                    anchors.fill: parent
                    spacing: 14

                    Rectangle {
                        Layout.preferredWidth: 350
                        Layout.fillHeight: true
                        radius: 10
                        color: root.panelColor
                        border.color: root.borderColor

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 14
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 9
                                Label {
                                    text: "Deliberately underdetermined"
                                    color: root.textPrimary
                                    font.pixelSize: 18
                                    font.bold: true
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "Three same-slice option prices attempt to identify five financial coordinates. M6 demonstrates that two starts can reach tiny loss yet materially different parameter estimates and rank-deficient local Jacobians."
                                    color: root.textMuted
                                    wrapMode: Text.WordWrap
                                }

                                Label { text: "Initial v₀"; color: root.textPrimary }
                                TextField {
                                    id: thinV0
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationInitialVariance
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial κ"; color: root.textPrimary }
                                TextField {
                                    id: thinKappa
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationKappa
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial θ"; color: root.textPrimary }
                                TextField {
                                    id: thinTheta
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationTheta
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial ξ"; color: root.textPrimary }
                                TextField {
                                    id: thinXi
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationXi
                                    onTextEdited: root.invalidate()
                                }
                                Label { text: "Initial ρ"; color: root.textPrimary }
                                TextField {
                                    id: thinRho
                                    Layout.fillWidth: true
                                    text: controller.defaultCalibrationRho
                                    onTextEdited: root.invalidate()
                                }

                                CheckBox {
                                    id: thinAdvanced
                                    text: "Advanced optimizer/numerical settings"
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    visible: thinAdvanced.checked
                                    Label { text: "Max function evaluations"; color: root.textPrimary }
                                    TextField {
                                        id: thinMaxEval
                                        Layout.fillWidth: true
                                        text: controller.defaultCalibrationMaxEvaluations
                                        onTextEdited: root.invalidate()
                                    }
                                    Label { text: "Heston Fourier intervals"; color: root.textPrimary }
                                    TextField {
                                        id: thinIntervals
                                        Layout.fillWidth: true
                                        text: controller.defaultCalibrationFourierIntervals
                                        onTextEdited: root.invalidate()
                                    }
                                }

                                Button {
                                    Layout.fillWidth: true
                                    text: controller.running ? "Calibration running…" : "Run thin calibration"
                                    enabled: !controller.running
                                    onClicked: controller.runHestonCalibration(
                                        "thin",
                                        thinV0.text,
                                        thinKappa.text,
                                        thinTheta.text,
                                        thinXi.text,
                                        thinRho.text,
                                        thinAdvanced.checked ? thinMaxEval.text : controller.defaultCalibrationMaxEvaluations,
                                        thinAdvanced.checked ? thinIntervals.text : controller.defaultCalibrationFourierIntervals
                                    )
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    radius: 8
                                    color: "#1f1608"
                                    border.color: root.warningColor
                                    implicitHeight: thinWarning.implicitHeight + 20
                                    Label {
                                        id: thinWarning
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 10
                                        text: "Scientific lesson: good price fit ≠ stable parameter estimate ≠ identified structural parameter."
                                        color: root.warningColor
                                        wrapMode: Text.WordWrap
                                        font.bold: true
                                    }
                                }
                            }
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        contentWidth: availableWidth
                        ColumnLayout {
                            width: parent.width
                            spacing: 12

                            Label { text: "Inverse problem"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationProblemModel
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
                            Label { text: "Two optimizer starts"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationRunModel
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
                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationParameterErrorPlotJson }
                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationObjectivePlotJson }
                            PlotCanvas { Layout.fillWidth: true; plotJson: controller.calibrationResidualPlotJson }
                            Label { text: "Identifiability evidence"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                            Repeater {
                                model: controller.calibrationConditioningModel
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

            Item {
                id: marketReferencePage
                ScrollView {
                    anchors.fill: parent
                    contentWidth: availableWidth

                    ColumnLayout {
                        width: parent.width
                        spacing: 12

                        Label { Layout.fillWidth: true; text: "Committed M6 SPX calibration reference"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Label {
                            Layout.fillWidth: true
                            text: "This is derived, package-safe evidence mirrored from the committed M6 reference artifact. The raw source rows are intentionally not redistributed; scripts/m6_heston_calibration.py remains the raw replay path."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }

                        Label { text: "Problem & market snapshot"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: controller.m6MarketSummaryModel
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

                        Label { text: "Provenance"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: controller.m6MarketProvenanceModel
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

                        Label { text: "Multiple-start outcomes"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: controller.m6MarketStartModel
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

                        PlotCanvas { Layout.fillWidth: true; plotJson: controller.m6MarketObjectivePlotJson }
                        PlotCanvas { Layout.fillWidth: true; plotJson: controller.m6MarketResidualPlotJson }

                        Label { text: "Best recorded result"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: controller.m6MarketResultModel
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

                        Label { text: "Conditioning & scientific limits"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                        Repeater {
                            model: controller.m6MarketConditioningModel
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

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 8
                            color: "#1f1608"
                            border.color: root.warningColor
                            implicitHeight: marketWarning.implicitHeight + 20
                            Label {
                                id: marketWarning
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 10
                                text: "No raw quote table, continuous surface, or M7 model-risk conclusion is fabricated here. M7 owns out-of-sample and Black-Scholes-vs-Heston comparison evidence."
                                color: root.warningColor
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
        }
    }
}
