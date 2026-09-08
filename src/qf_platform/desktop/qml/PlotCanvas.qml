import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property string plotJson: "{}"
    property var plotData: ({})
    property var seriesColors: ["#58a6ff", "#3fb950", "#d29922", "#bc8cff"]

    radius: 10
    color: "#161b22"
    border.color: "#30363d"
    border.width: 1
    implicitHeight: 360

    function refresh() {
        try {
            plotData = JSON.parse(plotJson || "{}")
        } catch (error) {
            plotData = ({})
        }
        canvas.requestPaint()
    }

    onPlotJsonChanged: refresh()
    Component.onCompleted: refresh()

    Label {
        id: titleLabel
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 16
        text: root.plotData.title || ""
        color: "#f0f6fc"
        font.pixelSize: 16
        font.bold: true
    }

    Canvas {
        id: canvas
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: titleLabel.bottom
        anchors.bottom: legend.top
        anchors.margins: 16

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.clearRect(0, 0, width, height)

            var series = root.plotData.series || []
            if (series.length === 0) {
                ctx.fillStyle = "#8b949e"
                ctx.font = "13px sans-serif"
                ctx.fillText("Run the study to populate this plot.", 20, 34)
                return
            }

            var xMin = Infinity
            var xMax = -Infinity
            var yMin = Infinity
            var yMax = -Infinity
            for (var s = 0; s < series.length; ++s) {
                var points = series[s].points || []
                for (var p = 0; p < points.length; ++p) {
                    var point = points[p]
                    xMin = Math.min(xMin, point.x)
                    xMax = Math.max(xMax, point.x)
                    yMin = Math.min(yMin, point.y)
                    yMax = Math.max(yMax, point.y)
                    if (point.lower !== null && point.lower !== undefined)
                        yMin = Math.min(yMin, point.lower)
                    if (point.upper !== null && point.upper !== undefined)
                        yMax = Math.max(yMax, point.upper)
                }
            }
            if (!isFinite(xMin) || !isFinite(yMin))
                return
            if (xMax === xMin) {
                xMin -= 0.5
                xMax += 0.5
            }
            if (yMax === yMin) {
                yMin -= 0.5
                yMax += 0.5
            }

            var xPad = 0.04 * (xMax - xMin)
            var yPad = 0.08 * (yMax - yMin)
            xMin -= xPad
            xMax += xPad
            yMin -= yPad
            yMax += yPad

            var left = 64
            var right = width - 18
            var top = 16
            var bottom = height - 48
            var plotWidth = Math.max(1, right - left)
            var plotHeight = Math.max(1, bottom - top)

            function px(x) {
                return left + (x - xMin) / (xMax - xMin) * plotWidth
            }
            function py(y) {
                return bottom - (y - yMin) / (yMax - yMin) * plotHeight
            }

            ctx.strokeStyle = "#30363d"
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(left, top)
            ctx.lineTo(left, bottom)
            ctx.lineTo(right, bottom)
            ctx.stroke()

            ctx.fillStyle = "#8b949e"
            ctx.font = "11px sans-serif"
            ctx.fillText(yMax.toPrecision(5), 4, top + 5)
            ctx.fillText(yMin.toPrecision(5), 4, bottom)
            ctx.fillText(xMin.toPrecision(5), left, height - 24)
            var xMaxText = xMax.toPrecision(5)
            ctx.fillText(xMaxText, right - 54, height - 24)
            ctx.fillText(root.plotData.xLabel || "", left, height - 5)

            for (var seriesIndex = 0; seriesIndex < series.length; ++seriesIndex) {
                var seriesPoints = series[seriesIndex].points || []
                var seriesColor = root.seriesColors[
                    seriesIndex % root.seriesColors.length
                ]
                ctx.strokeStyle = seriesColor
                ctx.fillStyle = seriesColor
                ctx.lineWidth = 2
                ctx.beginPath()
                for (var index = 0; index < seriesPoints.length; ++index) {
                    var item = seriesPoints[index]
                    var x = px(item.x)
                    var y = py(item.y)
                    if (index === 0)
                        ctx.moveTo(x, y)
                    else
                        ctx.lineTo(x, y)
                }
                ctx.stroke()

                ctx.lineWidth = 1
                for (var errorIndex = 0; errorIndex < seriesPoints.length; ++errorIndex) {
                    var errorPoint = seriesPoints[errorIndex]
                    if (errorPoint.lower === null || errorPoint.lower === undefined)
                        continue
                    if (errorPoint.upper === null || errorPoint.upper === undefined)
                        continue
                    var errorX = px(errorPoint.x)
                    var lowerY = py(errorPoint.lower)
                    var upperY = py(errorPoint.upper)
                    ctx.beginPath()
                    ctx.moveTo(errorX, lowerY)
                    ctx.lineTo(errorX, upperY)
                    ctx.moveTo(errorX - 4, lowerY)
                    ctx.lineTo(errorX + 4, lowerY)
                    ctx.moveTo(errorX - 4, upperY)
                    ctx.lineTo(errorX + 4, upperY)
                    ctx.stroke()
                }
            }
        }
    }

    Row {
        id: legend
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 14
        spacing: 18

        Repeater {
            model: root.plotData.series || []
            delegate: Row {
                required property var modelData
                required property int index
                spacing: 6
                Rectangle {
                    width: 12
                    height: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: root.seriesColors[index % root.seriesColors.length]
                }
                Label {
                    text: modelData.label || modelData.key || "Series"
                    color: "#8b949e"
                    font.pixelSize: 11
                }
            }
        }
    }
}
