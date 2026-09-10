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
        controller.invalidateUi4Result("heston")
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
        implicitHeight: cardColumn.implicitHeight + 22

        ColumnLayout {
            id: cardColumn
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
                    text: "Heston Forward Valuation"
                    color: root.textPrimary
                    font.pixelSize: 26
                    font.bold: true
                }
                Label {
                    Layout.fillWidth: true
                    text: "Same European-option pricing question, richer modeled state: (Sₜ, vₜ). Heston is the stochastic law; Fourier and Monte Carlo are independent valuation methods."
                    color: root.textMuted
                    wrapMode: Text.WordWrap
                }
            }
            Button {
                text: "Mathematics Inspector"
                onClicked: root.inspectorRequested()
            }
        }

        Label {
            Layout.fillWidth: true
            text: controller.status
            color: controller.running ? root.warningColor : root.textMuted
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            Rectangle {
                Layout.preferredWidth: 360
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
                            text: "Compose Heston Pricing Problem"
                            color: root.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "Guided financial inputs"
                            color: root.textMuted
                            font.pixelSize: 12
                        }

                        Label { text: "Spot S₀"; color: root.textPrimary }
                        TextField {
                            id: spotField
                            Layout.fillWidth: true
                            text: controller.defaultHestonSpot
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Strike K"; color: root.textPrimary }
                        TextField {
                            id: strikeField
                            Layout.fillWidth: true
                            text: controller.defaultHestonStrike
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Expiry"; color: root.textPrimary }
                        TextField {
                            id: expiryField
                            Layout.fillWidth: true
                            text: controller.defaultHestonExpiry
                            placeholderText: "YYYY-MM-DD"
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Current variance v₀"; color: root.textPrimary }
                        TextField {
                            id: v0Field
                            Layout.fillWidth: true
                            text: controller.defaultHestonInitialVariance
                            onTextEdited: root.invalidate()
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "v₀ is instantaneous variance, not volatility. v₀=0.04 corresponds to √v₀=0.20."
                            color: root.textMuted
                            font.pixelSize: 11
                            wrapMode: Text.WordWrap
                        }

                        Label { text: "Mean-reversion speed κ"; color: root.textPrimary }
                        TextField {
                            id: kappaField
                            Layout.fillWidth: true
                            text: controller.defaultHestonKappa
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Long-run variance θ"; color: root.textPrimary }
                        TextField {
                            id: thetaField
                            Layout.fillWidth: true
                            text: controller.defaultHestonTheta
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Volatility of variance ξ"; color: root.textPrimary }
                        TextField {
                            id: xiField
                            Layout.fillWidth: true
                            text: controller.defaultHestonXi
                            onTextEdited: root.invalidate()
                        }

                        Label { text: "Spot/variance correlation ρ"; color: root.textPrimary }
                        TextField {
                            id: rhoField
                            Layout.fillWidth: true
                            text: controller.defaultHestonRho
                            onTextEdited: root.invalidate()
                        }

                        CheckBox {
                            id: advancedCheck
                            text: "Advanced inputs & numerical methods"
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            visible: advancedCheck.checked
                            spacing: 8

                            Label { text: "Valuation date"; color: root.textPrimary }
                            TextField {
                                id: valuationDateField
                                Layout.fillWidth: true
                                text: controller.defaultHestonValuationDate
                                placeholderText: "YYYY-MM-DD"
                                onTextEdited: root.invalidate()
                            }

                            Label { text: "Continuously compounded rate r"; color: root.textPrimary }
                            TextField {
                                id: rateField
                                Layout.fillWidth: true
                                text: controller.defaultHestonRate
                                onTextEdited: root.invalidate()
                            }

                            Label { text: "Continuous dividend/carry q"; color: root.textPrimary }
                            TextField {
                                id: carryField
                                Layout.fillWidth: true
                                text: controller.defaultHestonCarry
                                onTextEdited: root.invalidate()
                            }

                            Label { text: "Option right"; color: root.textPrimary }
                            ComboBox {
                                id: rightBox
                                Layout.fillWidth: true
                                model: ["call", "put"]
                                currentIndex: controller.defaultHestonOptionRight === "put" ? 1 : 0
                                onActivated: root.invalidate()
                            }

                            Label { text: "Fourier integration lower / upper"; color: root.textPrimary }
                            RowLayout {
                                Layout.fillWidth: true
                                TextField {
                                    id: fourierLowerField
                                    Layout.fillWidth: true
                                    text: controller.defaultHestonFourierLower
                                    onTextEdited: root.invalidate()
                                }
                                TextField {
                                    id: fourierUpperField
                                    Layout.fillWidth: true
                                    text: controller.defaultHestonFourierUpper
                                    onTextEdited: root.invalidate()
                                }
                            }

                            Label { text: "Fourier Simpson intervals"; color: root.textPrimary }
                            TextField {
                                id: fourierIntervalsField
                                Layout.fillWidth: true
                                text: controller.defaultHestonFourierIntervals
                                onTextEdited: root.invalidate()
                            }

                            Label { text: "Monte Carlo paths / timesteps"; color: root.textPrimary }
                            RowLayout {
                                Layout.fillWidth: true
                                TextField {
                                    id: mcPathsField
                                    Layout.fillWidth: true
                                    text: controller.defaultHestonMonteCarloPaths
                                    onTextEdited: root.invalidate()
                                }
                                TextField {
                                    id: mcStepsField
                                    Layout.fillWidth: true
                                    text: controller.defaultHestonMonteCarloSteps
                                    onTextEdited: root.invalidate()
                                }
                            }

                            Label { text: "Monte Carlo seed"; color: root.textPrimary }
                            TextField {
                                id: mcSeedField
                                Layout.fillWidth: true
                                text: controller.defaultHestonMonteCarloSeed
                                onTextEdited: root.invalidate()
                            }

                            Label {
                                Layout.fillWidth: true
                                text: "Feller status is shown after normalization as a diagnostic only. Fourier truncation/quadrature and Monte Carlo sampling/time-discretization remain different numerical error sources."
                                color: root.textMuted
                                font.pixelSize: 11
                                wrapMode: Text.WordWrap
                            }
                        }

                        Button {
                            Layout.fillWidth: true
                            text: controller.running ? "Quantitative work running…" : "Run Fourier + Monte Carlo"
                            enabled: !controller.running
                            onClicked: controller.runHestonPricing(
                                spotField.text,
                                strikeField.text,
                                advancedCheck.checked ? valuationDateField.text : controller.defaultHestonValuationDate,
                                expiryField.text,
                                advancedCheck.checked ? rateField.text : controller.defaultHestonRate,
                                advancedCheck.checked ? carryField.text : controller.defaultHestonCarry,
                                advancedCheck.checked ? rightBox.currentText : controller.defaultHestonOptionRight,
                                v0Field.text,
                                kappaField.text,
                                thetaField.text,
                                xiField.text,
                                rhoField.text,
                                advancedCheck.checked ? fourierLowerField.text : controller.defaultHestonFourierLower,
                                advancedCheck.checked ? fourierUpperField.text : controller.defaultHestonFourierUpper,
                                advancedCheck.checked ? fourierIntervalsField.text : controller.defaultHestonFourierIntervals,
                                advancedCheck.checked ? mcPathsField.text : controller.defaultHestonMonteCarloPaths,
                                advancedCheck.checked ? mcStepsField.text : controller.defaultHestonMonteCarloSteps,
                                advancedCheck.checked ? mcSeedField.text : controller.defaultHestonMonteCarloSeed
                            )
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

                    Label { text: "Model composition"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                    Repeater {
                        model: controller.hestonModelModel
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

                    Label { text: "Heston financial coordinates"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                    Repeater {
                        model: controller.hestonParameterModel
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

                    Label { text: "Independent valuation evidence"; color: root.textPrimary; font.pixelSize: 18; font.bold: true }
                    Repeater {
                        model: controller.hestonResultModel
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

                    PlotCanvas { Layout.fillWidth: true; plotJson: controller.hestonMethodComparisonPlotJson }
                    PlotCanvas { Layout.fillWidth: true; plotJson: controller.hestonFourierStabilityPlotJson }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignTop
                            radius: 10
                            color: root.panelColor
                            border.color: root.borderColor
                            implicitHeight: fourierColumn.implicitHeight + 24
                            ColumnLayout {
                                id: fourierColumn
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 12
                                Label { text: "Fourier method"; color: root.textPrimary; font.bold: true }
                                Repeater {
                                    model: controller.hestonFourierModel
                                    delegate: ColumnLayout {
                                        required property string label
                                        required property string value
                                        required property string detail
                                        Layout.fillWidth: true
                                        Label { text: parent.label + ": " + parent.value; color: root.textPrimary; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        Label { text: parent.detail; color: root.textMuted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignTop
                            radius: 10
                            color: root.panelColor
                            border.color: root.borderColor
                            implicitHeight: mcColumn.implicitHeight + 24
                            ColumnLayout {
                                id: mcColumn
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 12
                                Label { text: "Monte Carlo method"; color: root.textPrimary; font.bold: true }
                                Repeater {
                                    model: controller.hestonMonteCarloModel
                                    delegate: ColumnLayout {
                                        required property string label
                                        required property string value
                                        required property string detail
                                        Layout.fillWidth: true
                                        Label { text: parent.label + ": " + parent.value; color: root.textPrimary; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        Label { text: parent.detail; color: root.textMuted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
