// Reusable smooth page-transition wrapper.
import QtQuick

Item {
    id: root
    default property alias content: inner.data
    property bool visible_: true
    anchors.fill: parent

    Item {
        id: inner
        anchors.fill: parent
        opacity: root.visible_ ? 1 : 0
        x: root.visible_ ? 0 : 12
        Behavior on opacity { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
        Behavior on x { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
    }
}
