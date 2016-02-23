# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Action Add Alerta AWIFs 2016
Description          : Action Add Alerta AWIFs 2016 by SQL
Date                 : February, 2016
copyright            : (C) 2016 by Luiz Motta
email                : motta.luiz@gmail.com

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
# CHANGE HERE for your target
#
feat_filter = '[% "geocodigo" %]'
#
nameModulus = "Action Add Alerta AWIFs 2016"
layerSQL = "alerta_awifs_2016_%s" % feat_filter
fileStyle = '/home/lmotta/data/qgis_qml/muni_alerta_awifs_2016.qml'
geomName = 'shape'
select = """
SELECT
  l.objectid,
  l.mes, l.ano,l."data_imagem",
  l.shape
FROM 
  "ibama"."alerta_awifs_2016_a" l
INNER JOIN 
  "cb"."lim_municipio_a" t
ON
  t.geocodigo = '%s' AND
  l.shape && t.geom AND
  ST_Intersects( l.shape, t.geom )
""" % feat_filter
#
#
# NOT CHANGE BELOW
#
from PyQt4.QtCore import QTimer, QFileInfo
from PyQt4.QtGui import QColor, QApplication

import qgis
from qgis.core import QgsDataSourceURI, QgsMapLayerRegistry, QgsSimpleLineSymbolLayerV2, QgsGeometry, QgsCoordinateTransform
from qgis.gui import QgsRubberBand, QgsMessageBar

class AddLayerSQL():
  def __init__(self, nameModulus, sqlProperties, layerSqlProperties):
    ( self.nameModulus, sqlProperties, layerSqlProperties ) =  ( nameModulus, sqlProperties, layerSqlProperties )
    #
    self.mlr = QgsMapLayerRegistry.instance()
    self.canvas = qgis.utils.iface.mapCanvas()
    #
    geom = QgsGeometry.fromWkt( sqlProperties[ 'geomWkt' ] )
    self.geomName = sqlProperties[ 'geomName' ]
    self.select = sqlProperties['select']
    self.layerSrc = self.mlr.mapLayer( sqlProperties[ 'layer_id' ] )
    #
    self.nameLayerSQL = layerSqlProperties[ 'name' ]
    self.fileStyleLayerSQL = layerSqlProperties[ 'fileStyle' ]
    #
    self.rb = self._highlightGeom( geom )

  def _highlightGeom(self, geom):
    def highlight():
      rb = QgsRubberBand( self.canvas, QGis.Polygon)
      rb.setBorderColor( QColor( 255,  0, 0 ) )
      rb.setWidth( 2 )
      rb.setToGeometry( geomRB, None )

      return rb

    crsCanvas = self.canvas.mapSettings().destinationCrs()
    crsLayer = self.layerSrc.crs()
    if not crsCanvas == crsLayer:
      geomRB = QgsGeometry( geom )
      ct = QgsCoordinateTransform( crsLayer, crsCanvas )
      geomRB.transform( ct )
    else:
      geomRB = geom

    return highlight()

  def _removeHighlight(self, seconds):
    def removeRB():
      self.rb.reset( True )
      self.canvas.scene().removeItem( self.rb )

    QTimer.singleShot( seconds * 1000, removeRB )

  def _addLayer(self, layer):
    def addStyle():
      fileStyle = QFileInfo( self.fileStyleLayerSQL )
      if fileStyle.exists() and fileStyle.isFile():
        layer.loadNamedStyle( self.fileStyleLayerSQL )

    msgBar = qgis.utils.iface.messageBar()
    if not layer.isValid():
      clip = QApplication.clipboard()
      clip.setText( self.select )
      msg = "Layer query '%s' not valid or no results. Query copied to Clipboard!" % self.nameLayerSQL
      msgBar.pushMessage( self.nameModulus, msg, QgsMessageBar.WARNING, 5 )
    else:
      msgBar.pushMessage( self.nameModulus, "Added %s" % self.nameLayerSQL, QgsMessageBar.INFO, 3 )
      addStyle()
      self.mlr.addMapLayer( layer )

    qgis.utils.iface.setActiveLayer( self.layerSrc )
    self._removeHighlight( 2 )

  def addLayer(self):
    schema = sql = keyCol = table = ''
    prov = self.layerSrc.dataProvider()
    name =  prov.name()
    uriSrc = QgsDataSourceURI( prov.dataSourceUri() )
    uri = QgsDataSourceURI()
    if uriSrc.host() == '':
      uri.setDatabase( uriSrc.database() )
      table = "( %s )" % self.select
    else:
      uri.setConnection( uriSrc.host(), uriSrc.port(), uriSrc.database(), uriSrc.username(), uriSrc.password() )
      keyCol = '_uid_'
      table = "( SELECT row_number() over () AS _uid_,* FROM ( %s ) AS _subq_1_ )" % self.select

    uri.setDataSource( schema, table, self.geomName, sql, keyCol )
    self._addLayer( QgsVectorLayer( uri.uri(), self.nameLayerSQL, name ) )
#
sqlProperties = { 'layer_id': '[% @layer_id %]', 'geomWkt': '[%geomToWKT(  $geometry  )%]', 'select': select, 'geomName': geomName }
layerSqlProperties = { 'name': layerSQL, 'fileStyle': fileStyle }
#
alq = AddLayerSQL( nameModulus, sqlProperties, layerSqlProperties )
alq.addLayer()