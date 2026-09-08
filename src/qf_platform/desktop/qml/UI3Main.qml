import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: hub
    width: 1180
    height: 780
    minimumWidth: 940
    minimumHeight: 620
    visible: true
    title: "Quant Research Workbench"
    color: "#0d1117"

    readonly property color panel: "#161b22"
    readonly property color border: "#30363d"
    readonly property color textPrimary: "#f0f6fc"
    readonly property color textMuted: "#8b949e"
    readonly property color good: "#3fb950"
    readonly property color warning: "#d29922"

    component WorkflowCard: Rectangle {
        required property string workflowTitle
        required property string workflowQuestion
        required property string workflowDetail
        required property string actionText
        signal launch()

        Layout.fillWidth: true
        radius: 12
        color: hub.panel
        border.color: hub.border
        border.width: 1
        implicitHeight: cardContent.implicitHeight + 40

        ColumnLayout {
            id: cardContent
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 20
            spacing: 10

            Label {
                text: parent.parent.workflowTitle
                color: hub.textPrimary
                font.pixelSize: 20
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.workflowQuestion
                color: hub.textPrimary
                font.pixelSize: 15
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.workflowDetail
                color: hub.textMuted
                wrapMode: Text.WordWrap
                font.pixelSize: 12
            }
            Button {
                text: parent.parent.actionText
                onClicked: parent.parent.launch()
            }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(940, hub.width - 80)
        spacing: 18

        Label {
            text: "Quant Research Workbench"
            color: hub.textPrimary
            font.pixelSize: 34
            font.bold: true
        }
        Label {
            Layout.fillWidth: true
            text: "Choose the mathematical question first. UI3 keeps valuation/sensitivity, model-generated control, and observed-market inference as distinct workflows rather than flattening them into one dashboard."
            color: hub.textMuted
            font.pixelSize: 16
            wrapMode: Text.WordWrap
        }

        WorkflowCard {
            workflowTitle: "Valuation & Sensitivity"
            workflowQuestion: "How do independent valuation methods compare, and how does value respond to inputs?"
            workflowDetail: "Existing UI2 workspace · Black-Scholes analytic / CRR / Monte Carlo · convergence · uncertainty · Delta / Gamma / Vega / Theta / Rho."
            actionText: "Open Valuation & Greeks"
            onLaunch: {
                hub.hide()
                valuationWindow.show()
            }
        }

        WorkflowCard {
            workflowTitle: "Dynamic Hedging / Control"
            workflowQuestion: "What did my hedge do through time, and why did replication fail?"
            workflowDetail: "M3 model-generated GBM paths · analytic-Delta policy · explicit stock/cash financing · rebalance-frequency, misspecification, replicate, and transaction-cost evidence."
            actionText: "Open Dynamic Hedging"
            onLaunch: {
                hub.hide()
                hedgeWindow.show()
            }
        }

        WorkflowCard {
            workflowTitle: "Market Evidence / Implied Volatility"
            workflowQuestion: "Which observed quote generated this implied volatility, how stable is the inversion, and what does the smile/skew show?"
            workflowDetail: "M4 raw synthetic observations + provenance · explicit normalization · bracketed Black-Scholes IV inversion · conditioning · pinned derived SPX strike/maturity evidence."
            actionText: "Open Market Evidence & IV"
            onLaunch: {
                hub.hide()
                marketWindow.show()
                if (!workbenchController.marketAnalysisReady)
                    workbenchController.loadMarketEvidence()
            }
        }

        Label {
            Layout.fillWidth: true
            text: "M5/Heston is merged but intentionally absent from UI3. UI4 should expose stochastic-volatility workflows only from actual merged M5/M6 contracts."
            color: hub.textMuted
            font.pixelSize: 12
            wrapMode: Text.WordWrap
        }
    }

    Main {
        id: valuationWindow
        visible: false
        onClosing: function(close) {
            hub.show()
        }
    }

    ApplicationWindow {
        id: hedgeWindow
        width: 1440
        height: 900
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Dynamic Hedging"
        color: "#0d1117"

        onClosing: function(close) {
            hub.show()
        }

        HedgeWorkspace {
            anchors.fill: parent
            controller: workbenchController
            panelColor: hub.panel
            borderColor: hub.border
            textPrimary: hub.textPrimary
            textMuted: hub.textMuted
            goodColor: hub.good
            warningColor: hub.warning
            onHomeRequested: {
                hedgeWindow.hide()
                hub.show()
            }
            onInspectorRequested: hedgeInspector.open()
        }

        Drawer {
            id: hedgeInspector
            width: Math.min(500, hedgeWindow.width * 0.42)
            height: hedgeWindow.height
            edge: Qt.RightEdge
            modal: false
            background: Rectangle { color: "#010409"; border.color: hub.border }

            ScrollView {
                anchors.fill: parent
                contentWidth: availableWidth
                ColumnLayout {
                    x: 18
                    y: 18
                    width: Math.max(0, parent.width - 36)
                    spacing: 12
                    Label { text: "Hedging Mathematical Inspector"; color: hub.textPrimary; font.pixelSize: 22; font.bold: true }
                    Label {
                        Layout.fillWidth: true
                        text: "State, generating law, Delta source, control policy, rebalance schedule, financing/cost convention, and replication objective remain explicit rather than hidden behind generic metadata."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.hedgeInspectorModel
                        delegate: Rectangle {
                            required property string label
                            required property string value
                            required property string detail
                            required property string status
                            Layout.fillWidth: true
                            radius: 8
                            color: hub.panel
                            border.color: hub.border
                            implicitHeight: hedgeInspectorCard.implicitHeight + 24
                            ColumnLayout {
                                id: hedgeInspectorCard
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 12
                                Label { text: parent.parent.label; color: hub.textPrimary; font.bold: true }
                                Label { Layout.fillWidth: true; text: parent.parent.value; color: hub.textPrimary; wrapMode: Text.WordWrap }
                                Label { Layout.fillWidth: true; text: parent.parent.detail; color: hub.textMuted; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                                Label { text: parent.parent.status; color: hub.good; font.pixelSize: 11 }
                            }
                        }
                    }
                }
            }
        }
    }

    ApplicationWindow {
        id: marketWindow
        width: 1440
        height: 900
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Market Evidence & Implied Volatility"
        color: "#0d1117"

        onClosing: function(close) {
            hub.show()
        }

        MarketWorkspace {
            anchors.fill: parent
            controller: workbenchController
            panelColor: hub.panel
            borderColor: hub.border
            textPrimary: hub.textPrimary
            textMuted: hub.textMuted
            goodColor: hub.good
            warningColor: hub.warning
            onHomeRequested: {
                marketWindow.hide()
                hub.show()
            }
            onInspectorRequested: marketInspector.open()
        }

        Drawer {
            id: marketInspector
            width: Math.min(500, marketWindow.width * 0.42)
            height: marketWindow.height
            edge: Qt.RightEdge
            modal: false
            background: Rectangle { color: "#010409"; border.color: hub.border }

            ScrollView {
                anchors.fill: parent
                contentWidth: availableWidth
                ColumnLayout {
                    x: 18
                    y: 18
                    width: Math.max(0, parent.width - 36)
                    spacing: 12
                    Label { text: "Inverse-Problem Mathematical Inspector"; color: hub.textPrimary; font.pixelSize: 22; font.bold: true }
                    Label {
                        Layout.fillWidth: true
                        text: "Observed target, forward model, unknown parameter, admissible domain, inverse numerical method, and conditioning evidence remain distinct."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.marketInspectorModel
                        delegate: Rectangle {
                            required property string label
                            required property string value
                            required property string detail
                            required property string status
                            Layout.fillWidth: true
                            radius: 8
                            color: hub.panel
                            border.color: hub.border
                            implicitHeight: marketInspectorCard.implicitHeight + 24
                            ColumnLayout {
                                id: marketInspectorCard
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 12
                                Label { text: parent.parent.label; color: hub.textPrimary; font.bold: true }
                                Label { Layout.fillWidth: true; text: parent.parent.value; color: hub.textPrimary; wrapMode: Text.WordWrap }
                                Label { Layout.fillWidth: true; text: parent.parent.detail; color: hub.textMuted; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                                Label { text: parent.parent.status; color: hub.good; font.pixelSize: 11 }
                            }
                        }
                    }
                }
            }
        }
    }
}
