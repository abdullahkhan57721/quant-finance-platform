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
    readonly property color panelRaised: "#1f2630"
    readonly property color border: "#30363d"
    readonly property color textPrimary: "#f0f6fc"
    readonly property color textMuted: "#8b949e"
    readonly property color accent: "#58a6ff"
    readonly property color good: "#3fb950"

    component SectionButton: Button {
        required property string sectionName
        text: sectionName
        Layout.fillWidth: true
        checkable: true
        checked: window.section === sectionName
        onClicked: window.section = sectionName
    }

    component Panel: Rectangle {
        radius: 10
        color: window.panel
        border.color: window.border
        border.width: 1
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
                    wrapMode: Text.WordWrap
                    color: window.textMuted
                    font.pixelSize: 17
                    text: "Compose mathematical-finance questions explicitly, run supported methods, and inspect the evidence behind the result."
                }
                Panel {
                    Layout.fillWidth: true
                    implicitHeight: homeContent.implicitHeight + 40
                    ColumnLayout {
                        id: homeContent
                        anchors.fill: parent
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
                            wrapMode: Text.WordWrap
                            color: window.textMuted
                            text: "European option · GBM / Black-Scholes · money-market Q semantics · analytic valuation"
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
                            color: window.textMuted
                            text: "Open Study persistence is intentionally deferred beyond UI1."
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
                        SectionButton { sectionName: "Compose" }
                        SectionButton { sectionName: "Analyze" }
                        SectionButton { sectionName: "Results" }
                        SectionButton { sectionName: "Validate" }
                        SectionButton { sectionName: "Present / Export" }
                        Item { Layout.fillHeight: true }
                        Button {
                            text: "Mathematical Inspector"
                            Layout.fillWidth: true
                            onClicked: inspectorDrawer.open()
                        }
                        Button {
                            text: "Home"
                            Layout.fillWidth: true
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
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 16
                                padding: 24
                                Label {
                                    text: "Compose"
                                    color: window.textPrimary
                                    font.pixelSize: 28
                                    font.bold: true
                                }
                                Label {
                                    Layout.fillWidth: true
                                    wrapMode: Text.WordWrap
                                    color: window.textMuted
                                    text: "Guided language maps to the same authoritative M1 semantics as Advanced disclosure. Inputs remain transient until Python validates them."
                                }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: formGrid.implicitHeight + 40
                                    GridLayout {
                                        id: formGrid
                                        anchors.fill: parent
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
                                            id: advancedToggle
                                            Layout.columnSpan: 2
                                            text: "Advanced semantics"
                                            checked: window.advanced
                                            onToggled: window.advanced = checked
                                        }
                                        FieldLabel { visible: window.advanced; text: "Valuation date" }
                                        TextField { id: valuationDateField; visible: window.advanced; Layout.fillWidth: true; text: workbenchController.defaultValuationDate; placeholderText: "YYYY-MM-DD" }
                                        FieldLabel { visible: window.advanced; text: "Model time" }
                                        Label { visible: window.advanced; color: window.textPrimary; text: "Actual/365 Fixed" }
                                        FieldLabel { visible: window.advanced; text: "Rate / carry semantics" }
                                        Label { visible: window.advanced; color: window.textPrimary; text: "Continuous annualized decimals" }
                                        FieldLabel { visible: window.advanced; text: "Pricing model / measure" }
                                        Label { visible: window.advanced; color: window.textPrimary; text: "Black-Scholes / GBM · Q^B money-market" }
                                        FieldLabel { visible: window.advanced; text: "Valuation method" }
                                        Label { visible: window.advanced; color: window.textPrimary; text: "Black-Scholes analytic" }
                                    }
                                }
                                RowLayout {
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
                                        color: window.textMuted
                                        wrapMode: Text.WordWrap
                                        text: workbenchController.status
                                    }
                                }
                            }
                        }

                        ScrollView {
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 16
                                padding: 24
                                Label { text: "Analyze"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Label {
                                    Layout.fillWidth: true
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                    text: "Terminal payoff is sampled in Python through the authoritative EuropeanOption.cash_flows contract. QML only maps renderer-neutral x/y values to pixels."
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
                                            ctx.reset()
                                            var points = JSON.parse(workbenchController.payoffPointsJson || "[]")
                                            if (points.length < 2) return
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
                                            ctx.beginPath(); ctx.moveTo(left, 8); ctx.lineTo(left, bottom); ctx.lineTo(width - 8, bottom); ctx.stroke()
                                            ctx.strokeStyle = window.accent
                                            ctx.lineWidth = 2.5
                                            ctx.beginPath()
                                            for (var j = 0; j < points.length; ++j) {
                                                var px = left + usableW * points[j].underlying / xMax
                                                var py = bottom - usableH * points[j].payoff / yMax
                                                if (j === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py)
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
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 18
                                padding: 24
                                Label { text: "Results"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: 180
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 24
                                        Label { text: "Present value"; color: window.textMuted; font.pixelSize: 13 }
                                        Label { text: workbenchController.presentValue; color: window.textPrimary; font.pixelSize: 42; font.bold: true }
                                        Label {
                                            Layout.fillWidth: true
                                            color: window.textMuted
                                            wrapMode: Text.WordWrap
                                            text: workbenchController.hasResult ? "Authoritative ValuationResult.present_value from merged M1." : "Run / Price to produce an authoritative valuation result."
                                        }
                                    }
                                }
                            }
                        }

                        ScrollView {
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 14
                                padding: 24
                                Label { text: "Validate"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Label {
                                    Layout.fillWidth: true
                                    color: window.textMuted
                                    wrapMode: Text.WordWrap
                                    text: "Capability, support, validation provenance, and Workbench exposure are deliberately distinct. Current-result checks are prepared in Python from normalized M1 semantics."
                                }
                                Repeater {
                                    model: workbenchController.evidenceModel
                                    delegate: Panel {
                                        required property string label
                                        required property string value
                                        required property string detail
                                        required property string status
                                        Layout.fillWidth: true
                                        implicitHeight: evidenceContent.implicitHeight + 28
                                        ColumnLayout {
                                            id: evidenceContent
                                            anchors.fill: parent
                                            anchors.margins: 14
                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label { Layout.fillWidth: true; text: parent.parent.parent.label; color: window.textPrimary; font.bold: true }
                                                Label { text: parent.parent.parent.status; color: window.good }
                                            }
                                            Label { Layout.fillWidth: true; text: parent.parent.value; color: window.textPrimary; wrapMode: Text.WordWrap }
                                            Label { Layout.fillWidth: true; text: parent.parent.detail; color: window.textMuted; wrapMode: Text.WordWrap }
                                        }
                                    }
                                }
                            }
                        }

                        ScrollView {
                            contentWidth: availableWidth
                            ColumnLayout {
                                width: parent.width
                                spacing: 16
                                padding: 24
                                Label { text: "Present / Export"; color: window.textPrimary; font.pixelSize: 28; font.bold: true }
                                Panel {
                                    Layout.fillWidth: true
                                    implicitHeight: 190
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 20
                                        Label { text: "Reference study summary"; color: window.textPrimary; font.pixelSize: 19; font.bold: true }
                                        Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: window.textMuted; text: "UI1 proves native presentation over authoritative M1 semantics. General reports, file export, and publication workflows remain future product work." }
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
                            verticalAlignment: Text.AlignVCenter
                            color: window.textMuted
                            elide: Text.ElideRight
                            text: workbenchController.status
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
            anchors.fill: parent
            ColumnLayout {
                width: parent.width
                spacing: 10
                padding: 20
                Label { text: "Mathematical Inspector"; color: window.textPrimary; font.pixelSize: 24; font.bold: true }
                Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: window.textMuted; text: "Read-only view of the active normalized pricing specification." }
                Repeater {
                    model: workbenchController.inspectorModel
                    delegate: ColumnLayout {
                        required property string label
                        required property string value
                        required property string detail
                        required property string status
                        Layout.fillWidth: true
                        spacing: 4
                        Label { text: parent.label; color: window.textMuted; font.pixelSize: 11; font.bold: true }
                        Label { Layout.fillWidth: true; text: parent.value; color: window.textPrimary; wrapMode: Text.WordWrap }
                        Label { Layout.fillWidth: true; text: parent.detail; color: window.textMuted; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                        Label { visible: parent.status !== ""; text: parent.status; color: window.good; font.pixelSize: 12 }
                        Rectangle { Layout.fillWidth: true; height: 1; color: window.border }
                    }
                }
            }
        }
    }
}
