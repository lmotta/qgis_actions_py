feat_filter = '[% "FIELD" %]' # Selected field from action - 'Pair of single quotes' for STRING field!
#
nameModulus = "ACTION NAME"
layerSQL = "LAYER NAME_%s" % feat_filter # Example for STRING field '%s'
fileStyle = '/PATH/STYLE NAME.qml'
geomName = 'GEOM NAME'
sql = """
PUT HERE SQL CODE!
...
"table"."feat_filter" = '%s'
...

""" % feat_filter
# Append Python script 'addlayersql.py' here
