import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1280
    height: 820
    minimumWidth: 1040
    minimumHeight: 680
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

    function validateCurrentDraft() {
        return workbenchController.validateDraft(
            spotField.text,
            strikeField.text,
            valuationDateField.text,
            expiryField.text,
            volatilityField.text,
            rateField.text,
            carryField.text,
            optionRight.currentText.toLowerCase()
        )
    }

    function priceCurrentDraft() {
        return workbenchController.priceDraft(
            spotField.text,
            strikeField.text,
            valuationDateField.text,
            expiryField.text,
            volatilityField.text,
            rateField.text,
            carryField.text,
            optionRight.currentText.toLowerCase()
        )
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: window.route === "home" ? 0 : 1

        Item {
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(720, window.width - 80)
                spacing: 22

                Label {
                    text: "Quant Research Workbench"
                    color: window.textPrimary
                    font.pixelSize: 34
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Compose mathematical-finance questions explicitly, run supported methods, and inspect the evidence behind the result."
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
                            text: "Black-Scholes reference study"
                            color: window.textPrimary
                            font.pixelSize: 20
                            font.bold: true
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "European option · GBM / Black-Scholes · money-market Q semantics · analytic valuation"
                            color: window.textMuted
                            wrapMode: Text.WordWrap
                        }
                        Button {
                            text: "New Study"
                            onClicked: {
                                window.route = "study"
                                window.section = "Compose"
                                window.validateCurrentDraft()
                            }
                        }
                        Label {
                            text: "Open Study persistence is intentionally deferred beyond UI1."
                            color: window.textMuted
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
                    Layout.preferredWidth: 210
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
                        Layout.preferredHeight: 72
                        color: window.panel
                        border.color: window.border
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            Label {
                                Layout.fillWidth: true
                                text: "European Option · Black-Scholes"
                                color: window.textPrimary
                                font.pixelSize: 21
                                font.bold: true
                            }
                            Label {
                                text: workbenchController.methodSupported ? "Analytic method supported" : "Validate composition"
                                color: workbenchController.methodSupported ? window.good : window.textMuted
                            }
                            Button {
                                text: workbenchController.running ? "Pricing…" : "Run / Price"
                                enabled: !workbenchController.running
                                onClicked: window.priceCurrentDraft()
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
                                    text: "Guided language maps to the same authoritative M1 semantics as Advanced disclosure. Inputs remain transient until Python validates them."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: composeGrid.implicitHeight + 40
                                    GridLayout {
                                        id: composeGrid
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 20
                                        columns: 2
                                        columnSpacing: 18
                                        rowSpacing: 12

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

                                        CheckBox {
                                            Layout.columnSpan: 2
                                            text: "Advanced semantics"
                                            checked: window.advanced
                                            onToggled: window.advanced = checked
                                        }
                                        FieldLabel { visible: window.advanced; text: "Valuation date" }
                                        TextField {
                                            id: valuationDateField
                                            visible: window.advanced
                                            Layout.fillWidth: true
                                            text: workbenchController.defaultValuationDate
                                            placeholderText: "YYYY-MM-DD"
                                        }
                                        FieldLabel { visible: window.advanced; text: "Model time" }
                                        Label { visible: window.advanced; text: "Actual/365 Fixed"; color: window.textPrimary }
                                        FieldLabel { visible: window.advanced; text: "Rate / carry semantics" }
                                        Label { visible: window.advanced; text: "Continuous annualized decimals"; color: window.textPrimary }
                                        FieldLabel { visible: window.advanced; text: "Pricing model / measure" }
                                        Label { visible: window.advanced; text: "Black-Scholes / GBM · Q^B money-market"; color: window.textPrimary }
                                        FieldLabel { visible: window.advanced; text: "Valuation method" }
                                        Label { visible: window.advanced; text: "Black-Scholes analytic"; color: window.textPrimary }
                                    }
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    Button {
                                        text: "Validate Composition"
                                        onClicked: window.validateCurrentDraft()
                                    }
                                    Button {
                                        text: "Price"
                                        enabled: !workbenchController.running
                                        onClicked: window.priceCurrentDraft()
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
                                    text: "Terminal payoff is sampled in Python through the authoritative EuropeanOption.cash_flows contract. QML only maps renderer-neutral x/y values to pixels."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }
                                Panel {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 420
                                    Canvas {
                                        id: payoffCanvas
                                        anchors.fill: parent
                                        anchors.margins: 24
                                        onPaint: {
                                            var ctx = getContext("2d")
                                            ctx.clearRect(0, 0, width, height)
                                            var points = JSON.parse(workbenchController.payoffPointsJson || "[]")
                                            if (points.length < 2)
                                                return
                                            var xMax = 1.0
                                            var yMax = 1.0
                                            for (var i = 0; i < points.length; ++i) {
                                                xMax = Math.max(xMax, points[i].underlying)
                                                yMax = Math.max(yMax, points[i].payoff)
                                            }
                                            var left = 44
                                            var bottom = height - 34
                                            var usableW = width - left - 16
                                            var usableH = bottom - 16
                                            ctx.strokeStyle = window.textMuted
                                            ctx.lineWidth = 1
                                            ctx.beginPath()
                                            ctx.moveTo(left, 8)
                                            ctx.lineTo(left, bottom)
                                            ctx.lineTo(width - 8, bottom)
                                            ctx.stroke()
                                            ctx.strokeStyle = window.accent
                                            ctx.lineWidth = 2.5
                                            ctx.beginPath()
                                            for (var j = 0; j < points.length; ++j) {
                                                var px = left + usableW * points[j].underlying / xMax
                                                var py = bottom - usableH * points[j].payoff / yMax
                                                if (j === 0)
                                                    ctx.moveTo(px, py)
                                                else
                                                    ctx.lineTo(px, py)
                                            }
                                            ctx.stroke()
                                        }
                                        Connections {
                                            target: workbenchController
                                            function onPresentationChanged() { payoffCanvas.requestPaint() }
                                        }
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
                                    implicitHeight: resultContent.implicitHeight + 48
                                    ColumnLayout {
                                        id: resultContent
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 24
                                        Label { text: "Present value"; color: window.textMuted; font.pixelSize: 13 }
                                        Label { text: workbenchController.presentValue; color: window.textPrimary; font.pixelSize: 42; font.bold: true }
                                        Label {
                                            Layout.fillWidth: true
                                            text: workbenchController.hasResult ? "Authoritative ValuationResult.present_value from merged M1." : "Run / Price to produce an authoritative valuation result."
                                            color: window.textMuted
                                            wrapMode: Text.WordWrap
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
                                    text: "Capability, support, validation provenance, and Workbench exposure are deliberately distinct. Current-result checks are prepared in Python from normalized M1 semantics."
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                }
                                Repeater {
                                    model: workbenchController.evidenceModel
                                    delegate: Panel {
                                        id: evidenceCard
                                        required property string label
                                        required property string value
                                        required property string detail
                                        required property string status
                                        Layout.fillWidth: true
                                        implicitHeight: evidenceContent.implicitHeight + 28
                                        ColumnLayout {
                                            id: evidenceContent
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 14
                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label { Layout.fillWidth: true; text: evidenceCard.label; color: window.textPrimary; font.bold: true }
                                                Label { text: evidenceCard.status; color: window.good }
                                            }
                                            Label { Layout.fillWidth: true; text: evidenceCard.value; color: window.textPrimary; wrapMode: Text.WordWrap }
                                            Label { Layout.fillWidth: true; text: evidenceCard.detail; color: window.textMuted; wrapMode: Text.WordWrap }
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
                                Label { text: "Present / Export"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: presentContent.implicitHeight + 40
                                    ColumnLayout {
                                        id: presentContent
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 20
                                        Label { text: "Reference study summary"; color: window.textPrimary; font.pixelSize: 19; font.bold: true }
                                        Label {
                                            Layout.fillWidth: true
                                            text: "UI1 proves native presentation over authoritative M1 semantics. General reports, file export, and publication workflows remain future product work."
                                            color: window.textMuted
                                            wrapMode: Text.WordWrap
                                        }
                                        Label { text: "PV: " + workbenchController.presentValue; color: window.textPrimary }
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 46
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
        edge: Qt.RightEdge
        width: Math.min(520, window.width * 0.46)
        height: window.height
        background: Rectangle { color: window.panel; border.color: window.border }

        ScrollView {
            id: inspectorScroll
            anchors.fill: parent
            clip: true
            contentWidth: availableWidth
            ColumnLayout {
                x: 20
                y: 20
                width: Math.max(0, inspectorScroll.availableWidth - 40)
                spacing: 10
                Label { text: "Mathematical Inspector"; color: window.textPrimary; font.pixelSize: 24; font.bold: true }
                Label {
                    Layout.fillWidth: true
                    text: "Read-only view of the active normalized pricing specification."
                    color: window.textMuted
                    wrapMode: Text.WordWrap
                }
                Repeater {
                    model: workbenchController.inspectorModel
                    delegate: ColumnLayout {
                        id: inspectorRow
                        required property string label
                        required property string value
                        required property string detail
                        required property string status
                        Layout.fillWidth: true
                        spacing: 4
                        Label { text: inspectorRow.label; color: window.textMuted; font.pixelSize: 11; font.bold: true }
                        Label { Layout.fillWidth: true; text: inspectorRow.value; color: window.textPrimary; wrapMode: Text.WordWrap }
                        Label { Layout.fillWidth: true; text: inspectorRow.detail; color: window.textMuted; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                        Label { visible: inspectorRow.status !== ""; text: inspectorRow.status; color: window.good; font.pixelSize: 12 }
                        Rectangle { Layout.fillWidth: true; height: 1; color: window.border }
                    }
                }
            }
        }
    }
}
