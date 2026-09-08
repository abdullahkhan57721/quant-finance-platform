import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1440
    height: 900
    minimumWidth: 1120
    minimumHeight: 720
    visible: true
    title: "Quant Research Workbench"
    color: "#0d1117"

    property string route: "home"
    property string section: "Compose"
    property bool advanced: false

    readonly property color panel: "#161b22"
    readonly property color border: "#30363d"
    readonly property color textPrimary: "#f0f6fc"
    readonly property color textMuted: "#8b949e"
    readonly property color accent: "#58a6ff"
    readonly property color good: "#3fb950"
    readonly property color warning: "#d29922"

    component Panel: Rectangle {
        radius: 10
        color: window.panel
        border.color: window.border
        border.width: 1
    }

    component NavButton: Button {
        required property string targetSection
        Layout.fillWidth: true
        text: targetSection
        checkable: true
        checked: window.section === targetSection
        onClicked: window.section = targetSection
    }

    component FieldLabel: Label {
        color: window.textMuted
        font.pixelSize: 12
    }

    component PresentationCard: Panel {
        required property string cardLabel
        required property string cardValue
        required property string cardDetail
        required property string cardStatus
        Layout.fillWidth: true
        implicitHeight: cardContent.implicitHeight + 28

        ColumnLayout {
            id: cardContent
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
                    color: window.textPrimary
                    font.bold: true
                }
                Label {
                    text: parent.parent.parent.cardStatus
                    color: window.good
                    font.pixelSize: 12
                }
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.cardValue
                color: window.textPrimary
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                text: parent.parent.cardDetail
                color: window.textMuted
                wrapMode: Text.WordWrap
                font.pixelSize: 12
            }
        }
    }

    function valuationMethodValue() {
        if (methodSelector.currentIndex === 1)
            return "crr"
        if (methodSelector.currentIndex === 2)
            return "monte_carlo"
        return "analytic"
    }

    function greekValue() {
        if (greekSelector.currentIndex === 1)
            return "gamma"
        if (greekSelector.currentIndex === 2)
            return "vega"
        if (greekSelector.currentIndex === 3)
            return "theta"
        if (greekSelector.currentIndex === 4)
            return "rho"
        return "delta"
    }

    function validateCurrentStudy() {
        return workbenchController.validateStudy(
            spotField.text,
            strikeField.text,
            valuationDateField.text,
            expiryField.text,
            volatilityField.text,
            rateField.text,
            carryField.text,
            optionRight.currentText.toLowerCase(),
            valuationMethodValue(),
            crrStepsField.text,
            monteCarloPathsField.text,
            monteCarloSeedField.text,
            greekValue(),
            spotBumpField.text,
            volatilityBumpField.text,
            rateBumpField.text,
            thetaDayBumpField.text
        )
    }

    function runCurrentStudy() {
        return workbenchController.runStudy(
            spotField.text,
            strikeField.text,
            valuationDateField.text,
            expiryField.text,
            volatilityField.text,
            rateField.text,
            carryField.text,
            optionRight.currentText.toLowerCase(),
            valuationMethodValue(),
            crrStepsField.text,
            monteCarloPathsField.text,
            monteCarloSeedField.text,
            greekValue(),
            spotBumpField.text,
            volatilityBumpField.text,
            rateBumpField.text,
            thetaDayBumpField.text
        )
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: window.route === "home" ? 0 : 1

        Item {
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(800, window.width - 96)
                spacing: 22

                Label {
                    text: "Quant Research Workbench"
                    color: window.textPrimary
                    font.pixelSize: 36
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Compose a Black-Scholes pricing question, compare independent valuation methods, inspect numerical convergence and Monte Carlo uncertainty, and study Greeks without moving quantitative meaning into the UI."
                    color: window.textMuted
                    font.pixelSize: 17
                    wrapMode: Text.WordWrap
                }
                Panel {
                    Layout.fillWidth: true
                    implicitHeight: homeContent.implicitHeight + 40

                    ColumnLayout {
                        id: homeContent
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 14

                        Label {
                            text: "Black-Scholes valuation & sensitivity study"
                            color: window.textPrimary
                            font.pixelSize: 21
                            font.bold: true
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "European option · analytic / CRR / Monte Carlo · convergence & sampling evidence · Delta / Gamma / Vega / Theta / Rho"
                            color: window.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Button {
                            text: "New Study"
                            onClicked: {
                                window.route = "study"
                                window.section = "Compose"
                                window.validateCurrentStudy()
                            }
                        }
                        Label {
                            text: "UI2 extends UI1; persistence and generic study schemas remain intentionally deferred."
                            color: window.textMuted
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }

        Item {
            RowLayout {
                anchors.fill: parent
                spacing: 0

                Rectangle {
                    Layout.preferredWidth: 220
                    Layout.fillHeight: true
                    color: "#010409"
                    border.color: window.border

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        Label {
                            text: "STUDY"
                            color: window.textMuted
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
                            onClicked: inspectorDrawer.open()
                        }
                        Button {
                            Layout.fillWidth: true
                            text: "Home"
                            onClicked: window.route = "home"
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 0

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 76
                        color: window.panel
                        border.color: window.border

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 14

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Label {
                                    text: "European Option · Black-Scholes"
                                    color: window.textPrimary
                                    font.pixelSize: 21
                                    font.bold: true
                                }
                                Label {
                                    text: "Selected method: " + workbenchController.selectedMethodLabel
                                    color: window.textMuted
                                    font.pixelSize: 12
                                }
                            }
                            Label {
                                text: workbenchController.methodSupported ? "Supported" : "Validate configuration"
                                color: workbenchController.methodSupported ? window.good : window.warning
                            }
                            Button {
                                text: workbenchController.running ? "Running…" : "Run Study"
                                enabled: !workbenchController.running
                                onClicked: window.runCurrentStudy()
                            }
                        }
                    }

                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: ["Compose", "Analyze", "Results", "Validate", "Present / Export"].indexOf(window.section)

                        ScrollView {
                            id: composeScroll
                            clip: true
                            contentWidth: availableWidth

                            ColumnLayout {
                                x: 24
                                y: 24
                                width: Math.max(0, composeScroll.availableWidth - 48)
                                spacing: 16

                                Label {
                                    text: "Compose"
                                    color: window.textPrimary
                                    font.pixelSize: 28
                                    font.bold: true
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: "Financial inputs normalize through the same M1 composition. Method, RNG, and finite-difference controls are separate UI2 configuration rather than financial state."
                                    color: window.textMuted
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

                                        Label {
                                            Layout.columnSpan: 2
                                            text: "Financial question"
                                            color: window.textPrimary
                                            font.pixelSize: 18
                                            font.bold: true
                                        }
                                        FieldLabel { text: "Spot" }
                                        TextField { id: spotField; Layout.fillWidth: true; text: workbenchController.defaultSpot }
                                        FieldLabel { text: "Strike" }
                                        TextField { id: strikeField; Layout.fillWidth: true; text: workbenchController.defaultStrike }
                                        FieldLabel { text: "Expiry" }
                                        TextField { id: expiryField; Layout.fillWidth: true; text: workbenchController.defaultExpiry; placeholderText: "YYYY-MM-DD" }
                                        FieldLabel { text: "Volatility" }
                                        TextField { id: volatilityField; Layout.fillWidth: true; text: workbenchController.defaultVolatility }
                                        FieldLabel { text: "Interest rate" }
                                        TextField { id: rateField; Layout.fillWidth: true; text: workbenchController.defaultRate }
                                        FieldLabel { text: "Dividend / carry" }
                                        TextField { id: carryField; Layout.fillWidth: true; text: workbenchController.defaultCarry }
                                        FieldLabel { text: "Option type" }
                                        ComboBox { id: optionRight; Layout.fillWidth: true; model: ["Call", "Put"] }
                                    }
                                }

                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: methodGrid.implicitHeight + 40

                                    GridLayout {
                                        id: methodGrid
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 20
                                        columns: 2
                                        columnSpacing: 18
                                        rowSpacing: 12

                                        Label {
                                            Layout.columnSpan: 2
                                            text: "Valuation method"
                                            color: window.textPrimary
                                            font.pixelSize: 18
                                            font.bold: true
                                        }
                                        FieldLabel { text: "Method" }
                                        ComboBox {
                                            id: methodSelector
                                            Layout.fillWidth: true
                                            model: ["Black-Scholes analytic", "Cox-Ross-Rubinstein", "Monte Carlo"]
                                        }
                                        FieldLabel { visible: methodSelector.currentIndex === 1; text: "CRR steps" }
                                        TextField {
                                            id: crrStepsField
                                            visible: methodSelector.currentIndex === 1
                                            Layout.fillWidth: true
                                            text: workbenchController.defaultCrrSteps
                                        }
                                        FieldLabel { visible: methodSelector.currentIndex === 2; text: "Monte Carlo paths" }
                                        TextField {
                                            id: monteCarloPathsField
                                            visible: methodSelector.currentIndex === 2
                                            Layout.fillWidth: true
                                            text: workbenchController.defaultMonteCarloPaths
                                        }
                                        FieldLabel { text: "Greek curve" }
                                        ComboBox {
                                            id: greekSelector
                                            Layout.fillWidth: true
                                            model: ["Delta", "Gamma", "Vega", "Theta", "Rho"]
                                        }
                                    }
                                }

                                CheckBox {
                                    text: "Advanced numerical / reproducibility controls"
                                    checked: window.advanced
                                    onToggled: window.advanced = checked
                                }

                                Panel {
                                    visible: window.advanced
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

                                        Label {
                                            Layout.columnSpan: 2
                                            text: "Advanced"
                                            color: window.textPrimary
                                            font.pixelSize: 18
                                            font.bold: true
                                        }
                                        FieldLabel { text: "Valuation date" }
                                        TextField {
                                            id: valuationDateField
                                            Layout.fillWidth: true
                                            text: workbenchController.defaultValuationDate
                                            placeholderText: "YYYY-MM-DD"
                                        }
                                        FieldLabel { text: "RNG seed" }
                                        TextField {
                                            id: monteCarloSeedField
                                            Layout.fillWidth: true
                                            text: workbenchController.defaultMonteCarloSeed
                                        }
                                        FieldLabel { text: "Spot bump" }
                                        TextField { id: spotBumpField; Layout.fillWidth: true; text: workbenchController.defaultSpotBump }
                                        FieldLabel { text: "Volatility bump" }
                                        TextField { id: volatilityBumpField; Layout.fillWidth: true; text: workbenchController.defaultVolatilityBump }
                                        FieldLabel { text: "Rate bump" }
                                        TextField { id: rateBumpField; Layout.fillWidth: true; text: workbenchController.defaultRateBump }
                                        FieldLabel { text: "Theta day bump" }
                                        TextField { id: thetaDayBumpField; Layout.fillWidth: true; text: workbenchController.defaultThetaDayBump }
                                        FieldLabel { text: "Model time" }
                                        Label { text: "Actual/365 Fixed"; color: window.textPrimary }
                                        FieldLabel { text: "Rates / carry" }
                                        Label { text: "Continuous annualized decimals"; color: window.textPrimary }
                                        FieldLabel { text: "Model / pricing measure" }
                                        Label { text: "Black-Scholes / GBM · Q^B money-market"; color: window.textPrimary }
                                        FieldLabel { text: "RNG semantics" }
                                        Label {
                                            Layout.fillWidth: true
                                            text: "Fresh local seeded Python RNG; reproducible within this implementation"
                                            color: window.textPrimary
                                            wrapMode: Text.WordWrap
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    Button {
                                        text: "Validate Study"
                                        enabled: !workbenchController.running
                                        onClicked: window.validateCurrentStudy()
                                    }
                                    Button {
                                        text: workbenchController.running ? "Running…" : "Run Study"
                                        enabled: !workbenchController.running
                                        onClicked: window.runCurrentStudy()
                                    }
                                    Label {
                                        Layout.fillWidth: true
                                        text: workbenchController.status
                                        color: window.textMuted
                                        wrapMode: Text.WordWrap
                                    }
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

                                Label { text: "Analyze"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Label {
                                    Layout.fillWidth: true
                                    text: "Plots consume renderer-neutral Python values. QML maps coordinates to pixels; it does not price options, calculate Greeks, confidence intervals, convergence error, or method compatibility."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: workbenchController.analysisReady ? "Completed UI2 evidence" : "Run the study to populate comparison and sensitivity plots."
                                    color: workbenchController.analysisReady ? window.good : window.textMuted
                                }

                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: analyzeScroll.availableWidth > 980 ? 2 : 1
                                    columnSpacing: 16
                                    rowSpacing: 16

                                    PlotCanvas {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 340
                                        plotJson: workbenchController.payoffPlotJson
                                    }
                                    PlotCanvas {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 340
                                        plotJson: workbenchController.crrPlotJson
                                    }
                                    PlotCanvas {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 340
                                        plotJson: workbenchController.monteCarloPlotJson
                                    }
                                    PlotCanvas {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 340
                                        plotJson: workbenchController.greekPlotJson
                                    }
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
                                spacing: 18

                                Label { text: "Results"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }

                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: selectedResult.implicitHeight + 40
                                    ColumnLayout {
                                        id: selectedResult
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 20
                                        spacing: 5
                                        Label { text: "Selected present value"; color: window.textMuted; font.pixelSize: 13 }
                                        Label { text: workbenchController.presentValue; color: window.textPrimary; font.pixelSize: 40; font.bold: true }
                                        Label { text: workbenchController.selectedMethodLabel; color: window.textMuted }
                                    }
                                }

                                Repeater {
                                    model: workbenchController.resultModel
                                    delegate: PresentationCard {
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

                                Label { text: "Valuation comparison"; color: window.textPrimary; font.pixelSize: 20; font.bold: true }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: valuationTable.implicitHeight + 28
                                    ColumnLayout {
                                        id: valuationTable
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 14
                                        spacing: 8

                                        GridLayout {
                                            Layout.fillWidth: true
                                            columns: 6
                                            columnSpacing: 10
                                            Label { text: "Method"; color: window.textMuted; font.bold: true }
                                            Label { text: "Configuration"; color: window.textMuted; font.bold: true }
                                            Label { text: "PV"; color: window.textMuted; font.bold: true }
                                            Label { text: "Δ analytic"; color: window.textMuted; font.bold: true }
                                            Label { text: "Evidence"; color: window.textMuted; font.bold: true }
                                            Label { text: "Status"; color: window.textMuted; font.bold: true }
                                        }
                                        Repeater {
                                            model: workbenchController.valuationComparisonModel
                                            delegate: GridLayout {
                                                required property string method
                                                required property string configuration
                                                required property string presentValue
                                                required property string difference
                                                required property string evidence
                                                required property string status
                                                Layout.fillWidth: true
                                                columns: 6
                                                columnSpacing: 10
                                                Label { text: parent.method; color: window.textPrimary; wrapMode: Text.WordWrap; Layout.preferredWidth: 140 }
                                                Label { text: parent.configuration; color: window.textMuted; wrapMode: Text.WordWrap; Layout.preferredWidth: 150 }
                                                Label { text: parent.presentValue; color: window.textPrimary; Layout.preferredWidth: 110 }
                                                Label { text: parent.difference; color: window.textPrimary; Layout.preferredWidth: 100 }
                                                Label { text: parent.evidence; color: window.textMuted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                Label { text: parent.status; color: window.good; Layout.preferredWidth: 90 }
                                            }
                                        }
                                    }
                                }

                                Label { text: "Greeks: analytic vs finite difference"; color: window.textPrimary; font.pixelSize: 20; font.bold: true }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: greekTable.implicitHeight + 28
                                    ColumnLayout {
                                        id: greekTable
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 14
                                        spacing: 8

                                        GridLayout {
                                            Layout.fillWidth: true
                                            columns: 6
                                            columnSpacing: 10
                                            Label { text: "Greek"; color: window.textMuted; font.bold: true }
                                            Label { text: "Analytic"; color: window.textMuted; font.bold: true }
                                            Label { text: "Finite diff"; color: window.textMuted; font.bold: true }
                                            Label { text: "Difference"; color: window.textMuted; font.bold: true }
                                            Label { text: "Units"; color: window.textMuted; font.bold: true }
                                            Label { text: "Status"; color: window.textMuted; font.bold: true }
                                        }
                                        Repeater {
                                            model: workbenchController.greekComparisonModel
                                            delegate: GridLayout {
                                                required property string greek
                                                required property string analytic
                                                required property string finiteDifference
                                                required property string difference
                                                required property string units
                                                required property string status
                                                Layout.fillWidth: true
                                                columns: 6
                                                columnSpacing: 10
                                                Label { text: parent.greek; color: window.textPrimary; Layout.preferredWidth: 90 }
                                                Label { text: parent.analytic; color: window.textPrimary; Layout.preferredWidth: 120 }
                                                Label { text: parent.finiteDifference; color: window.textPrimary; Layout.preferredWidth: 120 }
                                                Label { text: parent.difference; color: window.textPrimary; Layout.preferredWidth: 110 }
                                                Label { text: parent.units; color: window.textMuted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                Label { text: parent.status; color: window.good; Layout.preferredWidth: 110 }
                                            }
                                        }
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
                                spacing: 14

                                Label { text: "Validate"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Label {
                                    Layout.fillWidth: true
                                    text: "Structural meaning, implementation availability, selected-method support, validation evidence, and Workbench exposure remain separate. Finite-difference diagnostics preserve unsupported domain-crossing bumps rather than silently changing algorithms."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }

                                Label { text: "Compatibility"; color: window.textPrimary; font.pixelSize: 20; font.bold: true }
                                Repeater {
                                    model: workbenchController.compatibilityModel
                                    delegate: PresentationCard {
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

                                Label { text: "Finite-difference diagnostics"; color: window.textPrimary; font.pixelSize: 20; font.bold: true }
                                Repeater {
                                    model: workbenchController.finiteDifferenceModel
                                    delegate: PresentationCard {
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

                                Label { text: "M1 reference evidence"; color: window.textPrimary; font.pixelSize: 20; font.bold: true }
                                Repeater {
                                    model: workbenchController.evidenceModel
                                    delegate: PresentationCard {
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

                                Label { text: "Present / Export"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Label {
                                    Layout.fillWidth: true
                                    text: "UI2 records quantitative and numerical provenance needed to interpret the displayed result. Market-observation provenance remains out of scope until M4; general file export remains future product work."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }
                                Repeater {
                                    model: workbenchController.provenanceModel
                                    delegate: PresentationCard {
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
                        border.color: window.border
                        Label {
                            anchors.fill: parent
                            anchors.margins: 12
                            text: workbenchController.status
                            color: window.textMuted
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }
    }

    Drawer {
        id: inspectorDrawer
        width: Math.min(480, window.width * 0.42)
        height: window.height
        edge: Qt.RightEdge
        modal: false

        background: Rectangle {
            color: "#010409"
            border.color: window.border
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
                    text: "Mathematical Inspector"
                    color: window.textPrimary
                    font.pixelSize: 23
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "These values are derived in Python from the normalized financial problem; production object graphs remain private to Python."
                    color: window.textMuted
                    wrapMode: Text.WordWrap
                }
                Repeater {
                    model: workbenchController.inspectorModel
                    delegate: PresentationCard {
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
}