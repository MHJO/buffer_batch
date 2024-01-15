# -*- coding: utf-8 -*-
"""
/***************************************************************************
 screenshot_Dialog
                                 A QGIS plugin
 gis_my_tool
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-01-05
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
from functools import partial

from PyQt5.QtWidgets import (
    QFileDialog,QApplication,QMessageBox,QListView,QAbstractItemView,QTreeView
)
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import QTimer
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from qgis import processing
from qgis.utils import iface
from qgis.core import QgsFeatureRequest,QgsExpression

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__))+"/ui", 'screenshot_dialog_base.ui'))

class screenshot_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(screenshot_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self._map_canvas = iface.mapCanvas()

        self.setupUi(self)
        self.init_ui()
        self.listener()

    def init_ui(self):
        self.lb_layers.setText(self.tr("레이어명"))
        self.lb_attrs.setText(self.tr("속성 선택"))
        self.cbx_attrs.setVisible(False)
        self.lb_attrs.setVisible(False)
        self.rdo_allCap.setChecked(True)
        self.rdo_attrCap.setChecked(False)
        # self.txt_output.setText("") # 초기화
        # self.btn_refresh.setIcon(QIcon(':/plugins/buffer_batch/lib/img/refresh.png'))
        self.btn_refresh.setIcon(QIcon(':/plugins/buffer_batch/lib/img/refresh.png'))
        self.progressBar.setVisible(False)
        self.cmbSetting()
        self.changedSync()

    def listener(self):
        self.btn_refresh.clicked.connect(self.mapRefresh)
        self.btn_capture.clicked.connect(self.mapCapture)
        self.rdo_allCap.clicked.connect(self.changedSync)
        self.rdo_attrCap.clicked.connect(self.changedSync)

    def mapRefresh(self):
        self._map_canvas.refresh()
        self.cbx_layers.clear()
        self.cmbSetting()

    def changedSync(self):
        # # combo event
        # self.cbx_layers.currentIndexChanged.connect(self.getAttrs)
        # self.cbx_attrs.currentIndexChanged.connect(self.getAttrValue)
        if self.rdo_allCap.isChecked():
            print (1)
            self.lb_layers.setVisible(False)
            self.lb_attrs.setVisible(False)
            self.lb_func.setVisible(False)
            self.cbx_layers.setVisible(False)
            self.txt_func.setVisible(False)
            self.btn_refresh.setVisible(False)
        elif self.rdo_attrCap.isChecked():
            print (2)
            self.lb_layers.setVisible(True)
            self.lb_func.setVisible(True)
            self.cbx_layers.setVisible(True)
            self.txt_func.setVisible(True)
            self.btn_refresh.setVisible(True)

    def cmbSetting(self):
        # 레이어 목록을 가져옴
        self.getlyr = self.get_lyrList()
        self.cbx_layers.addItems(self.getlyr[0])
        # self.getAttrs()

    def get_lyrList(self):
        layersNames = ["선택"]
        layers = list()
        for i in self._map_canvas.layers():
            layersNames.append(str(i.name()))
            layers.append(i)
        return layersNames, layers

    def getAttrs(self):
        self.cbx_attrs.blockSignals(True)
        self.cbx_attrs.clear()
        if self.cbx_layers.currentIndex() !=0:
            layers = self.getlyr[1]
            idx = self.cbx_layers.currentIndex() -1

            header = [i.upper() for i in layers[idx].fields().names()]
            self.cbx_attrs.addItems(header)

    def getAttrValue(self):
        self.cbx_attrsV.blockSignals(True)
        self.cbx_attrsV.clear()
        layers = self.getlyr[1]
        idx = self.cbx_layers.currentIndex() - 1
        feats = layers[idx].getFeatures()
        attrList=list()
        for count, feat in enumerate(feats):
            attrList.append(feat[self.cbx_attrs.currentText()])
        self.cbx_attrsV.addItems(attrList)


    def saveMap(self,path):
        self._map_canvas.saveAsImage(path)

    # 화면 캡쳐
    def mapCapture(self):
        if self.rdo_allCap.isChecked():
            folder = QFileDialog.getExistingDirectory(None, "Select folder")
            if folder =="":
                return
            path = folder+"/allCap.png"
            try:
                self._map_canvas.saveAsImage(path)
                QMessageBox.information(None, "Alert", str(path)+"에 저장되었습니다.")
            except Exception as e:
                QMessageBox.warning(None, "DEBUG", str(e))
                return

        elif self.rdo_attrCap.isChecked():
            self.progressBar.setVisible(True)
            folder = QFileDialog.getExistingDirectory(None, "Select folder")
            try:
                self.progressBar.setVisible(True)
                self.progressBar.setValue(0)
                if self.cbx_layers.currentIndex() != 0:
                    layers = self.getlyr[1]
                    print ("currentText : ", self.cbx_layers.currentText())
                    for layer in layers:
                        if layer.name() == self.cbx_layers.currentText():
                            queryStr = self.txt_func.text()
                            request = QgsFeatureRequest(QgsExpression(queryStr)).setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([])
                            selection = layer.getFeatures(request)

                            selected_features = layer.selectedFeatures()
                            self.progressBar.setMaximum(len(selected_features))

                            # layer.selectByIds([s.id() for s in selection])
                            cnt = 0
                            for s in selection:
                                layer.selectByIds([s.id()])
                                QMessageBox.information(None, "Alert", "{}가 저장되었습니다.".format(str(s.id())))
                                self._map_canvas.zoomToSelected(layer)
                                self._map_canvas.refresh()

                                import time
                                time.sleep(2)

                                path = folder + "/{}.png".format(str(s.id()))
                                print (path)
                                self.saveMap(path)
                                # QTimer.singleShot(1000 * 5, saveMap)


                                cnt += 1
                                self.progressBar.setValue(cnt)


                QMessageBox.information(None, "Alert", str(folder)+"에 저장이 완료되었습니다.")
            except Exception as e:
                print (str(e))
                QMessageBox.warning(None, "DEBUG", str(e))
                return




