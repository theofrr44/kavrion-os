import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation
    Slide {
        Rectangle { anchors.fill: parent; color: "#0b1220" }
        Text {
            anchors.centerIn: parent; horizontalAlignment: Text.AlignHCenter
            color: "#22d3ee"; font.pixelSize: 28
            text: "Installation de KAVRION OS en cours…\nUn bureau léger, sombre et rapide."
        }
    }
}
