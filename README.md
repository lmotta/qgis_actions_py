<!-- IBAMA logo -->
[ibama_logo]: http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_IBAMA.svg/150px-Logo_IBAMA.svg.png

![][ibama_logo]  
[Brazilian Institute of Environment and Renewable Natural Resources](http://www.ibama.gov.br)

# QGIS Action Scripts

Use for Python Action in QGIS

## Author
Luiz Motta

## Scripts for Action that create Layer from SQL
* The layer with action need stay in database (Postgis or Spatialite)
* Create a layer with query.
* Works with 'addlayersql.py' and 'Header's script'

### addlayersql.py
* Main script for run SQL Query (Postgis and Spatialite) and create layer
* Use for join with 'Header's script'
* DON'T CHANGE this script

### create_action.sh
* Join 'addlayersql.py' with 'Header's script' and copy to Clipboard (paste this script in Layer's Action)
* Example: ./create_action header_add_landsat.py
* After run this script, paste code in Action property of layer

### model_action_add.py
* Model for define Header
* Variables:
  * feat_filter: Field from layer where use in SQL (use double quotes for String type)
  * nameModulus: Name this action for display in Message Bar
  * layerSQL: Name of layer that will be created by Action (use value of feat_filter)
  * fileStyle: Name of style file for layer
  * geomName: Name of geometry field in SELECT
  * sql: SQL with query, see type of filter field 

### header_add_deter_awifs_2016.py
* Example for Postgis

### header_add_landsat.py
* Example for Spatialite

## Changelog
- 2016-02-22
 Initial scripts for SQL Query

