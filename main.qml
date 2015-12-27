import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import Qt.labs.folderlistmodel 2.1

ApplicationWindow {
    id: app
    visible: true
    x: Screen.width / 2 - width / 2
    y: Screen.height / 2 - height / 2
    width: Screen.width * 0.7
    height: Screen.height * 0.7

    TreeView {
        id: project_tree
        anchors.fill: parent
        TableViewColumn {
            title: "Name"
            role: "display"
            width: 300
        }
        model: myModel
    }
}
