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

    property string section: "Compose"

    component Panel: Rectangle {
        radius: 10
        color: root.panelColor
        border.color: root.borderColor
        border.width: 1
    }

    component NavButton: Button {
        required property string targetSection
        Layout.fillWidth: true
        text: targetSection
        checkable: true
        checked: root.section === targetSection
        onClicked: root.section = targetSection
    }

    component Card: Panel {
        required property string cardLabel
        required property string cardValue
        required property string cardDetail
        required property string cardStatus
        Layout.fillWidth: true
        implicitHeight: content.implicitHeight + 28

        ColumnLayout {
            id: content
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 14
            spacing: 5
            RowLayout {
                Layout.fillWidth: true
                Label {
                    Layout.fillWidth: true
                    text: parent.parent.parent.cardLabel
                    color: root.textPrimary
                    font.bold: true
                }
                Label {
                    text: parent.parent.parent.cardStatus
                    color: root.goodColor
                    font.pixelSize: 12
                }
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.cardValue
                color: root.textPrimary
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.cardDetail
                color: root.textMuted
                wrapMode: Text.WordWrap
                font.pixelSize: 12
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 220
            Layout.fillHeight: true
            color: "#010409"
            border.color: root.borderColor

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 8
                Label {
                    text: "MARKET / INVERSE"
                    color: root.textMuted
                    font.pixelSize: 11
                    font.bold: true
                }
                NavButton { targetSection: "Compose" }
                NavButton { targetSection: "Analyze" }
                NavButton { targetSection: "Results" }
                NavButton { targetSection: "Validate" }
                NavButton { targetSection: "Present / Export" }
                Item { Layout.fillHeight: true }
                Button {
                    Layout.fillWidth: true
                    text: "Mathematical Inspector"
                    onClicked: root.inspectorRequested()
                }
                Button {
                    Layout.fillWidth: true
                    text: "Home"
                    onClicked: root.homeRequested()
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 82
                color: root.panelColor
                border.color: root.borderColor
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 14
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Label {
                            text: "Market Evidence & Implied Volatility · M4 Inverse Problem"
                            color: root.textPrimary
                            font.pixelSize: 21
                            font.bold: true
                        }
                        Label {
                            text: "Observed quote + provenance → normalization → inverse problem → implied volatility"
                            color: root.textMuted
                            font.pixelSize: 12
                        }
                    }
                    Label {
                        text: root.controller.marketAnalysisReady ? "Evidence ready" : "Load bundled M4 evidence"
                        color: root.controller.marketAnalysisReady ? root.goodColor : root.warningColor
                    }
                    Button {
                        text: root.controller.running ? "Running…" : "Load M4 Evidence"
                        enabled: !root.controller.running
                        onClicked: root.controller.loadMarketEvidence()
                    }
                }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: ["Compose", "Analyze", "Results", "Validate", "Present / Export"].indexOf(root.section)

                ScrollView {
                    id: composeScroll
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        x: 24
                        y: 24
                        width: Math.max(0, composeScroll.availableWidth - 48)
                        spacing: 16
                        Label { text: "Compose"; color: root.textPrimary; font.pixelSize: 28; font.bold: true }
                        Label {
                            Layout.fillWidth: true
                            text: "UI3 exposes two M4 evidence layers faithfully: a deterministic synthetic raw-observation laboratory that runs the actual normalization/inference pipeline, and pinned derived SPX smile/skew evidence whose upstream raw rows are intentionally not redistributed."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Panel {
                            Layout.fillWidth: true
                            implicitHeight: syntheticContent.implicitHeight + 40
                            ColumnLayout {
                                id: syntheticContent
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 20
                                spacing: 10
                                Label { text: "Synthetic raw-observation laboratory"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                                Label { Layout.fillWidth: true; text: "Underlying SYN · spot 100 · market date 2026-01-02 · two expiries · bid/ask quotes · explicit provenance"; color: root.textMuted; wrapMode: Text.WordWrap }
                                Label { Layout.fillWidth: true; text: "Model assumptions for inversion: continuously compounded r = 3%, continuous carry q = 1%, ACT/365F, volatility bracket [0, 5], bracketed bisection."; color: root.textMuted; wrapMode: Text.WordWrap }
                                Label { Layout.fillWidth: true; text: "Quote admissibility, midpoint normalization, price bounds, root solving, Vega, and conditioning remain Python/backend-owned."; color: root.textMuted; wrapMode: Text.WordWrap }
                            }
                        }
                        Panel {
                            Layout.fillWidth: true
                            implicitHeight: empiricalContent.implicitHeight + 40
                            ColumnLayout {
                                id: empiricalContent
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 20
                                spacing: 10
                                Label { text: "Pinned empirical SPX evidence"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                                Label { Layout.fillWidth: true; text: "January 4, 2023 SPX · two maturities · discrete strike slices · M4-derived implied volatilities and conditioning evidence."; color: root.textMuted; wrapMode: Text.WordWrap }
                                Label { Layout.fillWidth: true; text: "No raw SPX quote rows are redistributed. UI3 therefore does not pretend this panel is a raw-observation browser."; color: root.warningColor; wrapMode: Text.WordWrap }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Button {
                                text: root.controller.running ? "Running…" : "Load M4 Evidence"
                                enabled: !root.controller.running
                                onClicked: root.controller.loadMarketEvidence()
                            }
                            Label { Layout.fillWidth: true; text: root.controller.status; color: root.textMuted; wrapMode: Text.WordWrap }
                        }
                    }
                }

                ScrollView {
                    id: analyzeScroll
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        x: 24
                        y: 24
                        width: Math.max(0, analyzeScroll.availableWidth - 48)
                        spacing: 16
                        Label { text: "Analyze"; color: root.textPrimary; font.pixelSize: 28; font.bold: true }
                        Label {
                            Layout.fillWidth: true
                            text: "These are discrete strike/maturity slices. UI3 does not interpolate, smooth, or repair them into a volatility surface. Conditioning is plotted separately from root convergence."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        GridLayout {
                            Layout.fillWidth: true
                            columns: analyzeScroll.availableWidth > 980 ? 2 : 1
                            columnSpacing: 16
                            rowSpacing: 16
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.syntheticSmilePlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.syntheticConditioningPlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.empiricalSmilePlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.empiricalConditioningPlotJson }
                        }
                    }
                }

                ScrollView {
                    id: resultsScroll
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        x: 24
                        y: 24
                        width: Math.max(0, resultsScroll.availableWidth - 48)
                        spacing: 16
                        Label { text: "Results"; color: root.textPrimary; font.pixelSize: 28; font.bold: true }
                        Label {
                            Layout.fillWidth: true
                            text: "Select a synthetic quote to inspect exactly which raw observation generated the normalized target and implied volatility."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        ListView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 350
                            clip: true
                            model: root.controller.marketObservationModel
                            spacing: 4
                            delegate: Rectangle {
                                required property int index
                                required property string contractId
                                required property string expiry
                                required property string strike
                                required property string optionRight
                                required property string bid
                                required property string ask
                                required property string normalizedPrice
                                required property string impliedVolatility
                                required property string status
                                width: ListView.view.width
                                height: 54
                                color: index % 2 === 0 ? "#161b22" : "#0d1117"
                                border.color: root.borderColor
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    Label { text: parent.parent.contractId; color: root.textPrimary; Layout.preferredWidth: 160; elide: Text.ElideRight }
                                    Label { text: parent.parent.expiry; color: root.textMuted; Layout.preferredWidth: 95 }
                                    Label { text: parent.parent.optionRight + " K=" + parent.parent.strike; color: root.textMuted; Layout.preferredWidth: 120 }
                                    Label { text: "bid " + parent.parent.bid; color: root.textMuted; Layout.preferredWidth: 105 }
                                    Label { text: "ask " + parent.parent.ask; color: root.textMuted; Layout.preferredWidth: 105 }
                                    Label { text: "mid " + parent.parent.normalizedPrice; color: root.textMuted; Layout.preferredWidth: 110 }
                                    Label { text: "IV " + parent.parent.impliedVolatility; color: root.textPrimary; Layout.preferredWidth: 100 }
                                    Label { text: parent.parent.status; color: root.goodColor; Layout.fillWidth: true; elide: Text.ElideRight }
                                }
                                MouseArea { anchors.fill: parent; onClicked: root.controller.selectMarketObservation(index) }
                            }
                        }
                        Label { text: "Selected inverse result"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.marketInverseModel
                            delegate: Card {
                                required property string label
                                required property string value
                                required property string detail
                                required property string status
                                cardLabel: label
                                cardValue: value
                                cardDetail: detail
                                cardStatus: status
                            }
                        }
                    }
                }

                ScrollView {
                    id: validateScroll
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        x: 24
                        y: 24
                        width: Math.max(0, validateScroll.availableWidth - 48)
                        spacing: 16
                        Label { text: "Validate"; color: root.textPrimary; font.pixelSize: 28; font.bold: true }
                        Label {
                            Layout.fillWidth: true
                            text: "Observed diagnostics are not an arbitrage-repaired surface. Normalization and static strike diagnostics remain explicit evidence; UI3 does not modify the quotes."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Repeater {
                            model: root.controller.marketDiagnosticModel
                            delegate: Card {
                                required property string label
                                required property string value
                                required property string detail
                                required property string status
                                cardLabel: label
                                cardValue: value
                                cardDetail: detail
                                cardStatus: status
                            }
                        }
                        Label { text: "Pinned empirical M4 findings"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.marketEmpiricalSummaryModel
                            delegate: Card {
                                required property string label
                                required property string value
                                required property string detail
                                required property string status
                                cardLabel: label
                                cardValue: value
                                cardDetail: detail
                                cardStatus: status
                            }
                        }
                    }
                }

                ScrollView {
                    id: presentScroll
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        x: 24
                        y: 24
                        width: Math.max(0, presentScroll.availableWidth - 48)
                        spacing: 16
                        Label { text: "Present / Export"; color: root.textPrimary; font.pixelSize: 28; font.bold: true }
                        Label { text: "Selected synthetic raw-observation provenance"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.marketProvenanceModel
                            delegate: Card {
                                required property string label
                                required property string value
                                required property string detail
                                required property string status
                                cardLabel: label
                                cardValue: value
                                cardDetail: detail
                                cardStatus: status
                            }
                        }
                        Label { text: "Pinned empirical derived-evidence provenance"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.marketEmpiricalProvenanceModel
                            delegate: Card {
                                required property string label
                                required property string value
                                required property string detail
                                required property string status
                                cardLabel: label
                                cardValue: value
                                cardDetail: detail
                                cardStatus: status
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: "#010409"
                border.color: root.borderColor
                Label {
                    anchors.fill: parent
                    anchors.margins: 12
                    text: root.controller.status
                    color: root.textMuted
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            }
        }
    }
}
