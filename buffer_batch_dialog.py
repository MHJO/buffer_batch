# -*- coding: utf-8 -*-
"""
/***************************************************************************
 buffer_batchDialog
                                 A QGIS plugin
 buffer_batch
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-12-20
        git sha              : $Format:%H$
        copyright            : (C) 2023 by mh
        email                : mh.cho058@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import shutil

from PyQt5.QtWidgets import (
    QFileDialog,QApplication,QMessageBox,QListView,QAbstractItemView,QTreeView
)
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from qgis import processing

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'buffer_batch_dialog_base.ui'))


class buffer_batchDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(buffer_batchDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.init()

    def init(self):
        self.progressBar.setVisible(False)
        self.btn_input.clicked.connect(lambda : self.open_folder(self.txt_input))
        self.txt_dist.setText("3")
        # self.btn_output.clicked.connect()
        self.btn_run.clicked.connect(self.buffer_run)


    def open_folder(self, text):
        self.txt_result.setText("")
        try:
            # folder = QFileDialog.getExistingDirectory(self, "Select folder")
            # text.setText(folder)

            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.DirectoryOnly)
            file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            # file_view = file_dialog.findChild(QListView, 'listView')
            # to make it possible to select multiple directories:
            # if file_view:
            #    file_view.setSelectionMode(QAbstractItemView.MultiSelection)
            f_tree_view = file_dialog.findChild(QTreeView)
            if f_tree_view:
                f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

            if file_dialog.exec():
                folders = file_dialog.selectedFiles()
                
                check_list=list()
                for i in folders:
                    print (i,folders[0])
                    check_list.append(folders[0] in i)

                if len(folders) ==(check_list.count(True)):
                    folders1 = folders[1:]
                    print (folders1)
                else:
                    folders1= folders
                    print (folders1)
                text.setText(str(folders1).replace("[","").replace("]","").replace("'",""))
                QMessageBox.information(self,"선택폴더","선택된 폴더 : {0}".format(str(folders1)))


        except Exception as e:
            print (e.__str__())

    # batch 수행
    def buffer_run(self):
        inputPath = self.txt_input.text()
        QApplication.processEvents()
        print (inputPath.split(","))

        for folder in inputPath.split(","):
            i_folder=folder.strip()
            outputPath = os.path.dirname(i_folder) + "/{0}_output/".format(os.path.basename(i_folder))
            print (outputPath)
            self.txt_output.setText(outputPath)
            if os.path.exists(outputPath) != True:
                os.mkdir(outputPath)

            for layer in (os.listdir(i_folder)):
                if os.path.splitext(layer)[1] == ".shp":
                    layer_1 = i_folder + "/" + layer
                    output = outputPath + layer.replace(".shp", "_output.shp")
                    self.txt_result.setText("{0}\n수행중".format(output))

                    parameter = {
                        'INPUT': layer_1,
                        'DISSOLVE': False,
                        'DISTANCE': float(self.txt_dist.text()),
                        'END_CAP_STYLE': 0,
                        'JOIN_STYLE': 0,
                        'MITER_LIMIT': 2,
                        'SEGMENTS': 5,
                        'OUTPUT': output
                    }

                    try:
                        result = processing.run('qgis:buffer', parameter)
                        self.txt_result.setText("{0}\n생성 완료".format(output))

                        # # cpg 파일 생성 - EUC-KR
                        # if os.path.splitext(layer)[1] == ".cpg":
                        #     cpg_file = os.path.dirname(layer_1)
                        #     print (cpg_file)
                        #     if os.path.dirname(output).replace("shp","cpg") != True:
                        #         shutil.copy(cpg_file,os.path.dirname(output).replace("shp","cpg"))

                    except Exception as e:
                        print (e.__str__())
                        self.txt_result.setText("")
                        QMessageBox.warning(self, '오류', e.__str__())




