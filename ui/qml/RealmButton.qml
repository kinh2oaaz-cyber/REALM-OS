// Reusable premium button. Gold primary / crimson secondary. Smooth hover.
import QtQuick

Rectangle {
    id: btn
    property string text: ""
    property bool primary: true
    signal clicked()
    width: Math.max(96, label.implicitWidth + 32)
    height: 38
    radius: 10
    color: primary
        ? (mouse.containsMouse ? "#F1D58A" : "#D6AD55")
        : (mouse.containsMouse ? Qt.rgba(197/255,31/255,53/255,0.18) : Qt.rgba(28/255,21/255,25/255,0.72))
    border.color: primary ? "transparent" : Qt.rgba(214/255,173/255,85/255,0.22)
    border.width: primary ? 0 : 1

    Behavior on color { ColorAnimation { duration: 120 } }
    scale: mouse.pressed ? 0.97 : (mouse.containsMouse ? 1.02 : 1.0)
    Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutCubic } }

    Text {
        id: label
        anchors.centerIn: parent
        text: btn.text
        color: primary ? "#0B090B" : "#F5F0E9"
        font.pixelSize: 13
        font.weight: Font.DemiBold
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: btn.clicked()
    }
}
