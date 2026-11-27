// Reusable frosted-glass card. Original REALM; not Riot assets.
import QtQuick
import QtQuick.Effects

Rectangle {
    id: card
    color: Qt.rgba(28/255, 21/255, 25/255, 0.72)
    border.color: Qt.rgba(214/255, 173/255, 85/255, 0.18)
    border.width: 1
    radius: 14
    property bool hovered: false

    // subtle crimson ambient glow on hover + scale/elevation
    scale: hovered ? 1.015 : 1.0
    Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }

    Rectangle {
        anchors.fill: parent; radius: parent.radius; color: "transparent"
        border.color: hovered ? Qt.rgba(197/255, 31/255, 53/255, 0.45) : Qt.rgba(214/255,173/255,85/255,0.18)
        border.width: 1
        Behavior on border.color { ColorAnimation { duration: 140 } }
    }

    // soft edge lighting
    Rectangle {
        anchors { left: parent.left; right: parent.right; top: parent.top; leftMargin: radius; rightMargin: radius }
        height: 1; color: Qt.rgba(255,255,255, hovered ? 0.08 : 0.04)
        Behavior on color { ColorAnimation { duration: 140 } }
    }

    layer.enabled: true
    layer.effect: FastBlur { radius: 0 }   // no blur of content; card itself solid; background shows through via opacity
    opacity: 1.0
}
