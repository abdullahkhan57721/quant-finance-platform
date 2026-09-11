import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: hub
    width: 1220
    height: 860
    minimumWidth: 960
    minimumHeight: 680
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
        implicitHeight: cardContent.implicitHeight + 36

        ColumnLayout {
            id: cardContent
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 18
            spacing: 8

            Label {
                text: parent.parent.workflowTitle
                color: hub.textPrimary
                font.pixelSize: 19
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.workflowQuestion
                color: hub.textPrimary
                font.pixelSize: 14
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

    component InspectorCard: Rectangle {
        required property string rowLabel
        required property string rowValue
        required property string rowDetail
        required property string rowStatus
        Layout.fillWidth: true
        radius: 8
        color: hub.panel
        border.color: hub.border
        implicitHeight: inspectorColumn.implicitHeight + 24

        ColumnLayout {
            id: inspectorColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
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
                font.pixelSize: 12
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
            x: 40
            y: 34
            width: Math.max(0, parent.width - 80)
            spacing: 16

            Label {
                text: "Quant Research Workbench"
                color: hub.textPrimary
                font.pixelSize: 34
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                text: "UI4 makes model choice and inverse-problem composition explicit. Choose the mathematical question first; for forward valuation, Black-Scholes and Heston can price the same European contract while representing different stochastic state/law assumptions."
                color: hub.textMuted
                font.pixelSize: 15
                wrapMode: Text.WordWrap
            }

            Label {
                text: "Forward valuation — choose the modeled law"
                color: hub.textPrimary
                font.pixelSize: 18
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 14

                WorkflowCard {
                    workflowTitle: "Black-Scholes"
                    workflowQuestion: "What is this European option worth, and how sensitive is value to inputs?"
                    workflowDetail: "State Sₜ · constant volatility · UI2 analytic / CRR / Monte Carlo · Greeks. Contract and pricing question are independent of choosing this one-factor law."
                    actionText: "Open Black-Scholes"
                    onLaunch: {
                        hub.hide()
                        valuationWindow.show()
                    }
                }

                WorkflowCard {
                    workflowTitle: "Heston"
                    workflowQuestion: "What is the same kind of European pricing problem worth under stochastic variance?"
                    workflowDetail: "State (Sₜ, vₜ) · mean-reverting stochastic variance · correlated shocks · independent Fourier and Monte Carlo M5 methods with method-specific diagnostics."
                    actionText: "Open Heston Valuation"
                    onLaunch: {
                        hub.hide()
                        hestonWindow.show()
                    }
                }
            }

            Label {
                Layout.fillWidth: true
                text: "Changing Black-Scholes → Heston changes modeled state, stochastic law, and parameterization. It does not automatically change the European contract, pricing measure, or the fact that the question is forward valuation."
                color: hub.textMuted
                font.pixelSize: 12
                wrapMode: Text.WordWrap
            }

            Label {
                text: "Other mathematical workflows"
                color: hub.textPrimary
                font.pixelSize: 18
                font.bold: true
            }

            WorkflowCard {
                workflowTitle: "Heston Calibration / Inverse Problem"
                workflowQuestion: "Which Heston financial coordinates make forward model prices agree with selected price targets?"
                workflowDetail: "M6 price-space targets + weighting + financial bounds define CalibrationProblem; SciPy trust-region least squares is a separate optimizer. Includes truth recovery, rank-deficient counterexample, and the committed derived SPX reference."
                actionText: "Open Heston Calibration"
                onLaunch: {
                    hub.hide()
                    calibrationWindow.show()
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

            Rectangle {
                Layout.fillWidth: true
                radius: 8
                color: "#1f1608"
                border.color: hub.warning
                implicitHeight: boundaryNote.implicitHeight + 20
                Label {
                    id: boundaryNote
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 10
                    text: "UI4 does not manufacture Heston paths, implied-volatility-space calibration, optimizer progress, or M7 Black-Scholes-vs-Heston model-risk conclusions. Those require backend evidence that is not part of merged M5/M6."
                    color: hub.warning
                    wrapMode: Text.WordWrap
                }
            }
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
        id: hestonWindow
        width: 1460
        height: 920
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Heston Forward Valuation"
        color: "#0d1117"

        onClosing: function(close) {
            hub.show()
        }

        HestonWorkspace {
            anchors.fill: parent
            controller: workbenchController
            panelColor: hub.panel
            borderColor: hub.border
            textPrimary: hub.textPrimary
            textMuted: hub.textMuted
            goodColor: hub.good
            warningColor: hub.warning
            onHomeRequested: {
                hestonWindow.hide()
                hub.show()
            }
            onInspectorRequested: hestonInspector.open()
        }

        Drawer {
            id: hestonInspector
            width: Math.min(520, hestonWindow.width * 0.42)
            height: hestonWindow.height
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
                    Label { text: "Heston Pricing Mathematical Inspector"; color: hub.textPrimary; font.pixelSize: 22; font.bold: true }
                    Label {
                        Layout.fillWidth: true
                        text: "State, stochastic law, financial parameters, pricing measure, contract, pricing problem, valuation methods, and numerical assumptions remain explicit."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.hestonInspectorModel
                        delegate: InspectorCard {
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

    ApplicationWindow {
        id: calibrationWindow
        width: 1460
        height: 920
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Heston Calibration"
        color: "#0d1117"

        onClosing: function(close) {
            hub.show()
        }

        CalibrationWorkspace {
            anchors.fill: parent
            controller: workbenchController
            panelColor: hub.panel
            borderColor: hub.border
            textPrimary: hub.textPrimary
            textMuted: hub.textMuted
            goodColor: hub.good
            warningColor: hub.warning
            onHomeRequested: {
                calibrationWindow.hide()
                hub.show()
            }
            onInspectorRequested: calibrationInspector.open()
        }

        Drawer {
            id: calibrationInspector
            width: Math.min(540, calibrationWindow.width * 0.44)
            height: calibrationWindow.height
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
                    Label { text: "Calibration Mathematical Inspector"; color: hub.textPrimary; font.pixelSize: 22; font.bold: true }
                    Label {
                        Layout.fillWidth: true
                        text: "Targets, unknowns, forward operator, objective, weights, financial bounds, inverse numerical method, immutable result, and local conditioning remain separate."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.calibrationInspectorModel
                        delegate: InspectorCard {
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

    ApplicationWindow {
        id: hedgeWindow
        width: 1440
        height: 900
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Dynamic Hedging"
        color: "#0d1117"

        onClosing: function(close) { hub.show() }

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
                        text: "State, generating law, Delta source, control policy, rebalance schedule, financing/cost convention, and replication objective remain explicit."
                        color: hub.textMuted
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: workbenchController.hedgeInspectorModel
                        delegate: InspectorCard {
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

    ApplicationWindow {
        id: marketWindow
        width: 1440
        height: 900
        minimumWidth: 1120
        minimumHeight: 720
        visible: false
        title: "Quant Research Workbench · Market Evidence & Implied Volatility"
        color: "#0d1117"

        onClosing: function(close) { hub.show() }

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
                        delegate: InspectorCard {
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
}
