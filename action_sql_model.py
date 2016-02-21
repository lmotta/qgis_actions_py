# Values from each features -- NOT CHANGE!
#
layer_id = '[% @layer_id %]'
feat_id = [% "fid" %]
geomWkt = '[%geomToWKT(  $geometry  )%]'
#
# CHANGE HERE for your target
#
nameModulus = "ACTION NAME"
layerSQL = "LAYER NAME_%d" % feat_id # Add number of FID
fileStyle = '/PATH/STYLE NAME.qml'
geomName = 'GEOM NAME'
select = """(
PUT HERE SQL CODE!
)""" % feat_id
#
#
# NOT CHANGE BELOW
#
from PyQt4.QtCore import QTimer, QFileInfo
from PyQt4.QtGui import QColor

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
    msgBar.pushMessage( self.nameModulus, "Adding %s" % self.nameLayerSQL, QgsMessageBar.INFO, 2 )
    addStyle()
    self.mlr.addMapLayer( layer )
    qgis.utils.iface.setActiveLayer( self.layerSrc )
    self._removeHighlight( 2 )

  def addQueryByPG(self):
    dataSourceUri = self.layerSrc.dataProvider().dataSourceUri()
    uriSrc = QgsDataSourceURI( dataSourceUri )
    uri = QgsDataSourceURI()
    uri.setConnection( uriSrc.host(), uriSrc.port(), uriSrc.database(), uriSrc.username(), uriSrc.password() )
    uri.setDataSource( uriSrc.schema(), self.select, self.geomName )
    #
    self._addLayer( QgsVectorLayer( uri.uri(), self.nameLayerSQL, 'postgres') )

  def addQueryBySqlite(self):
    dataSourceUri = self.layerSrc.dataProvider().dataSourceUri()
    schema = ''
    uri = QgsDataSourceURI()
    uri.setDatabase( dataSourceUri.split('|')[0] )
    uri.setDataSource( schema, self.select, self.geomName )
    #
    self._addLayer( QgsVectorLayer( uri.uri(), self.nameLayerSQL, 'spatialite' ) )
#
sqlProperties = { 'layer_id': layer_id, 'geomWkt': geomWkt, 'select': select, 'geomName': geomName }
layerSqlProperties = { 'name': layerSQL, 'fileStyle': fileStyle }
#
alq = AddLayerSQL( nameModulus, sqlProperties, layerSqlProperties )
alq.addQueryBySqlite()
