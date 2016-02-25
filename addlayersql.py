#
"""
/***************************************************************************
Name                 : AddLayerSQL
Description          : Class for add Layer by SQL use for Action in QGIS.
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
#
import codecs, os

import psycopg2
from pyspatialite import dbapi2 as sqlite

from PyQt4.QtCore import QTimer, QFileInfo
from PyQt4.QtGui import QColor, QApplication

import qgis
from qgis.core import (
    QgsApplication,
    QgsDataSourceURI, QgsMapLayerRegistry,
    QgsGeometry, QgsCoordinateTransform
)
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
    self.styleLayerSQL = layerProperties[ 'style' ]

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
      tableStyle = 'layer_styles'
      tConn = ( uri.host(), uri.port(), uri.username(), uri.password(), uri.database() )
      sConn = "host='%s' port='%s' user='%s' password='%s' dbname='%s'" % tConn
      driver = psycopg2
      sql = "SELECT EXISTS( SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '%s' )" % tableStyle
      return { 
        'driver': driver,
        'conn': psycopg2.connect( sConn ),
        'sqlStyleTable': sql,
        'tableStyle': tableStyle
      }

    def connectSqlite( uri ):
      tableStyle = 'layer_styles'
      sConn = uri.database()
      driver = sqlite
      sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % tableStyle
      return { 
        'driver': driver,
        'conn': sqlite.connect( sConn ),
        'sqlStyleTable': sql,
        'tableStyle': tableStyle
      }

    def runSQL(sql, cur, drv_conn):
      msgError = None
      try:
        cur.execute( sql )
      except drv_conn['driver'].Error as e:
        msgError = e.message
      #
      if not msgError is None:
        clip = QApplication.clipboard()
        msg = "Error in query '%s'.\nError: %s\n\n%s" % ( self.nameLayerSQL, msgError, sql ) 
        clip.setText( msg.decode( 'utf-8') )
        msg = "Error in query '%s'. See Clipboard!" % self.nameLayerSQL
        cur.close()
        drv_conn['conn'].close()
        return { 'isOk': False, 'msg': msg }
      return { 'isOk': True }

    def existFeatures():
      drv_conn = f_connections[ name ]( uri )
      cur = drv_conn['conn'].cursor()
      #
      result = runSQL( self.sql, cur, drv_conn )
      if not result['isOk']:
        return result
      #
      hasFeatures = False if cur.fetchone() is None else True
      #
      cur.close()
      drv_conn['conn'].close()

      return { 'isOk': True, 'hasFeatures': hasFeatures }

    def addStyleLayerQuery():
      def getStyleDB():
        drv_conn = f_connections[ name ]( uri )
        cur = drv_conn['conn'].cursor()
        #
        result = runSQL( drv_conn[ 'sqlStyleTable' ], cur, drv_conn )
        if not result[ 'isOk']:
          return result
        #
        hasTable = False if cur.fetchone() is None else True
        if hasTable is None:
          data = ( self.nameLayerSQL, drv_conn[ 'tableStyle' ] )
          msg = "Error in query '%s' (for verify style). Not exist table '%s'!" % data
          return { 'isOk': True, 'exits': False, 'msg': msg }
        #
        data = ( drv_conn[ 'tableStyle' ], self.styleLayerSQL )
        sql = "SELECT styleQML FROM %s WHERE styleName = '%s'" % data
        result = runSQL( sql, cur, drv_conn )
        if not result[ 'isOk']:
          return result
        #
        value = cur.fetchone()
        if value is None:
          data = ( self.nameLayerSQL, self.styleLayerSQL, rv_conn[ 'tableStyle' ] )
          msg = "Error in query '%s' (for verify style). Not exist style '%s' in table '%s'!" % data
          return { 'isOk': True, 'exits': False, 'msg': msg }
        #
        cur.close()
        drv_conn['conn'].close()
        #
        return { 'isOk': True, 'exits': True, 'qml': value[0] }
        #

      def setStyleLayer(qml):
        qmlFile = "%saddlayersql_action_temp.qml" % ( QgsApplication.qgisSettingsDirPath() )
        if os.path.exists(qmlFile):
          os.remove( qmlFile )
        f = codecs.open( qmlFile, 'w', encoding='utf8')
        f.write( qml )
        f.close()
        #
        layerQuery.loadNamedStyle( qmlFile )
        #
        os.remove( qmlFile )

      if self.styleLayerSQL is None:
        return
      # File
      fileStyle = QFileInfo( self.styleLayerSQL )
      if fileStyle.exists() and fileStyle.isFile():
        layerQuery.loadNamedStyle( self.styleLayerSQL )
        return
      # DB *** Had self.styleLayerSQL and not is file -> Need be a DB
      result = getStyleDB()
      if not result['isOk'] or not result['exits']:
        rb = self._addHighlightGeom()
        self.msgBar.pushMessage( self.nameModulus, result['msg'], QgsMessageBar.WARNING, 5 )
        self._removeHighlightGeom( rb, 5 )
        return
      #
      setStyleLayer( result['qml'] )

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
sqlProperties = { 
  'layer_id': '[% @layer_id %]', 
  'geomWkt': '[%geomToWKT(  $geometry  )%]',
  'sql': sql,
  'geomName': geomName
}
layerProperties = { 'name': layerSQL, 'style': style }
#
alq = AddLayerSQL( nameModulus, sqlProperties, layerProperties )
alq.addLayer()
