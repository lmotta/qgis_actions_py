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
