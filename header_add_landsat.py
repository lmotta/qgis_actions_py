feat_filter = '[% "geocodmu" %]' # Value from action "geocodmu" is STRING!
#
nameModulus = "Action Add Landsat"
layerSQL = "landsat_muni_%s" % feat_filter
style = 'add_landsat'
geomName = 'geom'
sql = """
SELECT
  "img_catalogo_landsat"."id",
  "img_catalogo_landsat"."image",
  "img_catalogo_landsat"."data",
  "img_catalogo_landsat"."orbita",
  "img_catalogo_landsat"."ponto",
  "img_catalogo_landsat"."geom" 
FROM 
  "img_catalogo_landsat"
INNER JOIN 
  "municipio_ibge"
ON
  "municipio_ibge"."geocodmu" = '%s' AND
  MbrIntersects("img_catalogo_landsat"."geom", "municipio_ibge"."geom") AND
  ST_Intersects("img_catalogo_landsat"."geom", "municipio_ibge"."geom")
""" % feat_filter
#
