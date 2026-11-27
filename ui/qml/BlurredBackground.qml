// Reusable Qt Quick blurred background — REALM crimson x gold, near-black.
// Real Qt Quick blur (QtQuick.Effects.FastBlur), NOT a static transparent rect.
// Performance-safe: no animation on the blur; cached layer; software backend OK.
import QtQuick
import QtQuick.Effects

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        id: base
        anchors.fill: parent
        color: "#0B090B"
    }

    // subtle dark crimson ambient gradient
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#140A0C" }
            GradientStop { position: 0.5; color: "#141014" }
            GradientStop { position: 1.0; color: "#0B090B" }
        }
    }

    Item {
        id: lights
        anchors.fill: parent
        layer.enabled: true

        // subtle blurred red + gold light sources (desaturated)
        Rectangle {
            x: parent.width * 0.58; y: parent.height * 0.06
            width: parent.width * 0.5; height: parent.height * 0.5
            color: "#A82435"; opacity: 0.10
            radius: width / 2
        }
        Rectangle {
            x: parent.width * 0.5; y: parent.height * 0.55
            width: parent.width * 0.55; height: parent.height * 0.5
            color: "#C9A863"; opacity: 0.08
            radius: width / 2
        }
        Rectangle {
            x: 0; y: parent.height * 0.45
            width: parent.width * 0.4; height: parent.height * 0.6
            color: "#7A1A2A"; opacity: 0.12
            radius: width / 2
        }

        layer.effect: FastBlur {
            radius: 64
            transparentBorder: true
        }
    }
}