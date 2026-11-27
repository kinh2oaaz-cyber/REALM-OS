// Animated loading indicator. Gold ring on crimson. Smooth, lightweight.
import QtQuick

Item {
    id: root
    width: 32; height: 32
    property color accent: "#C9A863"

    Rectangle {
        id: ring
        anchors.fill: parent
        color: "transparent"
        border.color: Qt.rgba(214/255,173/255,85/255,0.18)
        border.width: 3; radius: width / 2
    }
    Rectangle {
        width: 8; height: 8; radius: 4; color: accent
        anchors.horizontalCenter: parent.horizontalCenter
        y: -2
    }
    RotationAnimation on rotation {
        from: 0; to: 360; duration: 900; loops: Animation.Infinite; running: root.visible
    }
}
