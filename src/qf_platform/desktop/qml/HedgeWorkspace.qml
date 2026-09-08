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
    property bool advanced: false

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

    function runHedge() {
        return root.controller.runHedgeStudy(
            spotField.text,
            strikeField.text,
            valuationDateField.text,
            expiryField.text,
            rateField.text,
            optionRight.currentText.toLowerCase(),
            generatingVolField.text,
            hedgingVolField.text,
            rebalanceField.text,
            seedField.text,
            replicateField.text,
            transactionCostField.text
        )
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
                    text: "DYNAMIC HEDGING"
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
                            text: "Dynamic Delta Hedging · M3 Control"
                            color: root.textPrimary
                            font.pixelSize: 21
                            font.bold: true
                        }
                        Label {
                            text: "Model-generated path → Delta policy → realized hedge → replication evidence"
                            color: root.textMuted
                            font.pixelSize: 12
                        }
                    }
                    Label {
                        text: root.controller.hedgeAnalysisReady ? "Evidence ready" : "Configure study"
                        color: root.controller.hedgeAnalysisReady ? root.goodColor : root.warningColor
                    }
                    Button {
                        text: root.controller.running ? "Running…" : "Run Hedge Study"
                        enabled: !root.controller.running
                        onClicked: root.runHedge()
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
                            text: "Research question: how do rebalance frequency, volatility misspecification, and transaction costs affect replication? M3 currently supports zero continuous dividend yield for hedge execution."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Panel {
                            Layout.fillWidth: true
                            implicitHeight: financialGrid.implicitHeight + 40
                            GridLayout {
                                id: financialGrid
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 20
                                columns: 2
                                columnSpacing: 18
                                rowSpacing: 12
                                Label { Layout.columnSpan: 2; text: "European option"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                                Label { text: "Spot"; color: root.textMuted }
                                TextField { id: spotField; Layout.fillWidth: true; text: root.controller.defaultSpot }
                                Label { text: "Strike"; color: root.textMuted }
                                TextField { id: strikeField; Layout.fillWidth: true; text: root.controller.defaultStrike }
                                Label { text: "Valuation date"; color: root.textMuted }
                                TextField { id: valuationDateField; Layout.fillWidth: true; text: root.controller.defaultValuationDate }
                                Label { text: "Expiry"; color: root.textMuted }
                                TextField { id: expiryField; Layout.fillWidth: true; text: root.controller.defaultExpiry }
                                Label { text: "Interest rate"; color: root.textMuted }
                                TextField { id: rateField; Layout.fillWidth: true; text: root.controller.defaultRate }
                                Label { text: "Option type"; color: root.textMuted }
                                ComboBox { id: optionRight; Layout.fillWidth: true; model: ["Call", "Put"] }
                                Label { text: "Dividend / carry"; color: root.textMuted }
                                Label { text: "0 (M3 supported execution boundary)"; color: root.textPrimary }
                            }
                        }
                        Panel {
                            Layout.fillWidth: true
                            implicitHeight: researchGrid.implicitHeight + 40
                            GridLayout {
                                id: researchGrid
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 20
                                columns: 2
                                columnSpacing: 18
                                rowSpacing: 12
                                Label { Layout.columnSpan: 2; text: "Hedge experiment"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                                Label { text: "World generating volatility"; color: root.textMuted }
                                TextField { id: generatingVolField; Layout.fillWidth: true; text: root.controller.defaultGeneratingVolatility }
                                Label { text: "Hedge-assumed volatility"; color: root.textMuted }
                                TextField { id: hedgingVolField; Layout.fillWidth: true; text: root.controller.defaultHedgingVolatility }
                                Label { text: "Rebalance every N days"; color: root.textMuted }
                                TextField { id: rebalanceField; Layout.fillWidth: true; text: root.controller.defaultRebalanceDayInterval }
                                Label { text: "Proportional transaction-cost rate"; color: root.textMuted }
                                TextField { id: transactionCostField; Layout.fillWidth: true; text: root.controller.defaultTransactionCostRate }
                            }
                        }
                        CheckBox {
                            text: "Advanced reproducibility controls"
                            checked: root.advanced
                            onToggled: root.advanced = checked
                        }
                        Panel {
                            visible: root.advanced
                            Layout.fillWidth: true
                            implicitHeight: advancedGrid.implicitHeight + 40
                            GridLayout {
                                id: advancedGrid
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 20
                                columns: 2
                                columnSpacing: 18
                                rowSpacing: 12
                                Label { Layout.columnSpan: 2; text: "Advanced"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                                Label { text: "Selected path seed"; color: root.textMuted }
                                TextField { id: seedField; Layout.fillWidth: true; text: root.controller.defaultHedgeSeed }
                                Label { text: "Replicate count"; color: root.textMuted }
                                TextField { id: replicateField; Layout.fillWidth: true; text: root.controller.defaultHedgeReplicateCount }
                                Label { text: "Path observation grid"; color: root.textMuted }
                                Label { text: "Daily; exact adjacent GBM transitions"; color: root.textPrimary }
                                Label { text: "Comparison design"; color: root.textMuted }
                                Label { Layout.fillWidth: true; text: "Same seeded paths reused across hedge conditions"; color: root.textPrimary; wrapMode: Text.WordWrap }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Button {
                                text: root.controller.running ? "Running…" : "Run Hedge Study"
                                enabled: !root.controller.running
                                onClicked: root.runHedge()
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
                            text: "The selected path is one realization. Aggregate replication evidence below is computed across distinct seeded paths; QML only renders Python-prepared series."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        GridLayout {
                            Layout.fillWidth: true
                            columns: analyzeScroll.availableWidth > 980 ? 2 : 1
                            columnSpacing: 16
                            rowSpacing: 16
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeUnderlyingPlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeValuePlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeDeltaPlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeCashPlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeFrequencyPlotJson }
                            PlotCanvas { Layout.fillWidth: true; Layout.preferredHeight: 340; plotJson: root.controller.hedgeReplicatePlotJson }
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
                        Label { text: "Selected path terminal accounting"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.hedgeResultModel
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
                        Label { text: "Rebalance trajectory — select a row"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        ListView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 260
                            clip: true
                            model: root.controller.hedgeStepModel
                            spacing: 4
                            delegate: Rectangle {
                                required property int index
                                required property string time
                                required property string spot
                                required property string optionValue
                                required property string stockUnits
                                required property string hedgeValue
                                width: ListView.view.width
                                height: 42
                                color: index % 2 === 0 ? "#161b22" : "#0d1117"
                                border.color: root.borderColor
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    Label { text: time; color: root.textPrimary; Layout.preferredWidth: 100 }
                                    Label { text: "S " + spot; color: root.textMuted; Layout.preferredWidth: 100 }
                                    Label { text: "V " + optionValue; color: root.textMuted; Layout.preferredWidth: 110 }
                                    Label { text: "Δ " + stockUnits; color: root.textMuted; Layout.preferredWidth: 110 }
                                    Label { text: "H " + hedgeValue; color: root.textMuted; Layout.fillWidth: true }
                                }
                                MouseArea { anchors.fill: parent; onClicked: root.controller.selectHedgeStep(index) }
                            }
                        }
                        Label { text: "Selected rebalance"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.hedgeSelectedStepModel
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
                            text: "A dramatic selected path is not a scientific conclusion. These summaries compare repeated terminal replication evidence under controlled changes."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Repeater {
                            model: root.controller.hedgeAggregateModel
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
                        Label { text: "Rebalance-frequency evidence"; color: root.textPrimary; font.pixelSize: 20; font.bold: true }
                        Repeater {
                            model: root.controller.hedgeFrequencyModel
                            delegate: Panel {
                                required property string cadence
                                required property string replicates
                                required property string meanError
                                required property string errorStandardDeviation
                                required property string meanAbsoluteError
                                required property string rootMeanSquareError
                                Layout.fillWidth: true
                                implicitHeight: 78
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    Label { text: parent.parent.cadence; color: root.textPrimary; font.bold: true; Layout.preferredWidth: 150 }
                                    Label { text: "n=" + parent.parent.replicates; color: root.textMuted; Layout.preferredWidth: 60 }
                                    Label { text: "mean " + parent.parent.meanError; color: root.textMuted; Layout.preferredWidth: 130 }
                                    Label { text: "sd " + parent.parent.errorStandardDeviation; color: root.textMuted; Layout.preferredWidth: 130 }
                                    Label { text: "MAE " + parent.parent.meanAbsoluteError; color: root.textMuted; Layout.preferredWidth: 130 }
                                    Label { text: "RMSE " + parent.parent.rootMeanSquareError; color: root.textPrimary; Layout.fillWidth: true }
                                }
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
                        Label {
                            Layout.fillWidth: true
                            text: "Hedge evidence records model-generation, RNG, observation/rebalance, volatility, financing, and transaction-cost semantics. File export remains future product work."
                            color: root.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Repeater {
                            model: root.controller.hedgeProvenanceModel
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
