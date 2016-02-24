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
sql = """
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
import psycopg2
from pyspatialite import dbapi2 as sqlite

from PyQt4.QtCore import QTimer, QFileInfo
from PyQt4.QtGui import QColor, QApplication

import qgis
from qgis.core import QgsDataSourceURI, QgsMapLayerRegistry, QgsSimpleLineSymbolLayerV2, QgsGeometry, QgsCoordinateTransform
from qgis.gui import QgsRubberBand, QgsMessageBar

class AddLayerSQL():
  def __init__(self, nameModulus, sqlProperties, layerProperties):
    self.nameModulus =  nameModulus
    #
    self.mlr = QgsMapLayerRegistry.instance()
    self.canvas = qgis.utils.iface.mapCanvas()
    self.msgBar = qgis.utils.iface.messageBar()
    #
    self.geom = QgsGeometry.fromWkt( sqlProperties[ 'geomWkt' ] )
    self.geomName = sqlProperties[ 'geomName' ]
    self.sql = sqlProperties['sql']
    self.layerSrc = self.mlr.mapLayer( sqlProperties[ 'layer_id' ] )
    #
    self.nameLayerSQL = layerProperties[ 'name' ]
    self.fileStyleLayerSQL = layerProperties[ 'fileStyle' ]

  def _addHighlightGeom(self):
    def highlight():
      rb = QgsRubberBand( self.canvas, QGis.Polygon)
      rb.setBorderColor( QColor( 255,  0, 0 ) )
      rb.setWidth( 2 )
      rb.setToGeometry( geomRB, None )

      return rb

    crsCanvas = self.canvas.mapSettings().destinationCrs()
    crsLayer = self.layerSrc.crs()
    if not crsCanvas == crsLayer:
      geomRB = QgsGeometry( self.geom )
      ct = QgsCoordinateTransform( crsLayer, crsCanvas )
      geomRB.transform( ct )
    else:
      geomRB = self.geom

    return highlight()

  def _removeHighlightGeom(self, rb, seconds):
    def removeRB():
      rb.reset( True )
      self.canvas.scene().removeItem( rb )

    QTimer.singleShot( seconds * 1000, removeRB )

  def addLayer(self):
    def connectPostgres( uri ):
      tConn = ( uri.host(), uri.port(), uri.username(), uri.password(), uri.database() )
      sConn = "host='%s' port='%s' user='%s' password='%s' dbname='%s'" % tConn
      driver = psycopg2
      return { 'driver': driver, 'conn': psycopg2.connect( sConn ) }

    def connectSqlite( uri ):
      sConn = uri.database()
      driver = sqlite
      return { 'driver': driver, 'conn': sqlite.connect( sConn ) }

    def existFeatures():
      drv_conn = f_connections[ name ]( uri )
      cur = drv_conn['conn'].cursor()
      #
      msgError = None
      try:
        cur.execute( self.sql )
      except drv_conn['driver'].Error as e:
        msgError = e.message
      #
      if not msgError is None:
        clip = QApplication.clipboard()
        msg = "Error in query '%s'.\nError: %s\n\n%s" % ( self.nameLayerSQL, msgError, self.sql ) 
        clip.setText( msg.decode( 'utf-8') )
        msg = "Error in query '%s'. See Clipboard!" % self.nameLayerSQL
        cur.close()
        drv_conn['conn'].close()
        return { 'isOk': False, 'msg': msg }
      #
      hasFeatures = False if cur.fetchone() is None else True
      #
      cur.close()
      drv_conn['conn'].close()

      return { 'isOk': True, 'hasFeatures': hasFeatures }

    def addStyleLayerQuery():
      fileStyle = QFileInfo( self.fileStyleLayerSQL )
      if fileStyle.exists() and fileStyle.isFile():
        layerQuery.loadNamedStyle( self.fileStyleLayerSQL )

    f_connections = { 'postgres': connectPostgres, 'spatialite': connectSqlite }
    prov = self.layerSrc.dataProvider()
    name =  prov.name()
    if not name in f_connections.keys():
      msg = "Provider '%s' of layer '%s' is not supported!" % ( name, self.layerSrc.name() )
      self.msgBar.pushMessage( self.nameModulus, msg, QgsMessageBar.WARNING, 5 )
      return

    keyCol = table = ''
    uri = QgsDataSourceURI( prov.dataSourceUri() )
    if uri.host() == '':
      table = "( %s )" % self.sql
    else:
      keyCol = '_uid_'
      table = "( SELECT row_number() over () AS _uid_,* FROM ( %s ) AS _subq_1_ )" % self.sql

    result = existFeatures()
    if not result['isOk']:
      rb = self._addHighlightGeom()
      self.msgBar.pushMessage( self.nameModulus, result['msg'], QgsMessageBar.WARNING, 5 )
      self._removeHighlightGeom( rb, 5 )
      return
    if not result['hasFeatures']:
      rb = self._addHighlightGeom()
      msg = "Not found features in query '%s'!"  % self.nameLayerSQL
      self.msgBar.pushMessage( self.nameModulus, msg, QgsMessageBar.WARNING, 5 )
      self._removeHighlightGeom( rb, 5 )
      return

    schema = filter_sql = ''
    uri.setDataSource( schema, table, self.geomName, filter_sql, keyCol )
    layerQuery = QgsVectorLayer( uri.uri(), self.nameLayerSQL, name )
    if not layerQuery.isValid(): # Never happing?
      rb = self._addHighlightGeom()
      msg = "Layer query '%s' not valid!" % self.nameLayerSQL
      self.msgBar.pushMessage( self.nameModulus, msg, QgsMessageBar.WARNING, 5 )
      self._removeHighlightGeom( rb, 2 )
      return

    msg = "Added %s (total %s)" % ( self.nameLayerSQL, layerQuery.featureCount() )
    self.msgBar.pushMessage( self.nameModulus, msg, QgsMessageBar.INFO, 3 )
    rb = self._addHighlightGeom()
    addStyleLayerQuery()
    self.mlr.addMapLayer( layerQuery )
    qgis.utils.iface.setActiveLayer( self.layerSrc )
    self._removeHighlightGeom( rb, 2 )
#
sqlProperties = { 'layer_id': '[% @layer_id %]', 'geomWkt': '[%geomToWKT(  $geometry  )%]', 'sql': sql, 'geomName': geomName }
layerProperties = { 'name': layerSQL, 'fileStyle': fileStyle }
#
alq = AddLayerSQL( nameModulus, sqlProperties, layerProperties )
alq.addLayer()
