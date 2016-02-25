feat_filter = '[% "FIELD" %]' # Selected field from action - 'Pair of single quotes' for STRING field!
#
nameModulus = "ACTION NAME"
layerSQL = "LAYER NAME_%s" % feat_filter # Example for STRING field '%s'
#
# Style: None, QML file or name style for DB (Sqlite or  Postgres)
# - None: style = None
# - QML file: style = 'FILE.qml'
# - Name of style in DB: style = 'name_style'
#   * Search in 'layer_styles' table and the 'styleQML' field
#   ** Postgres use 'public' Schema
style = None
#
geomName = 'GEOM NAME'
sql = """
PUT HERE SQL CODE!
...
"table"."feat_filter" = '%s'
...

""" % feat_filter
# Append Python script 'addlayersql.py' here
