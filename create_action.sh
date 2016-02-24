#!/bin/bash
#
# ***************************************************************************
# Name                 : create_action
# Description          : Join 'header action.py' and 'addlayer.py' and put in Clipboard
# Arguments            : Name file of 'header action.py'
# Dependencies         : xclip
#
#                       -------------------
# begin                : 2016-02-23
# copyright            : (C) 2016 by Luiz Motta
# email                : motta dot luiz at gmail.com
# ***************************************************************************
# 
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************
#
#
msg_error(){
  local name_script=$(basename $0)
  echo "Usage: $name_script <file_name>" >&2
  echo "<file_name> is the file's name of 'header action.py'" >&2
  exit 1
}
#
totalargs=1
#
if [ $# -ne $totalargs ] ; then
  msg_error
  exit 1
fi
#
in_file=$1
#
if [ ! -f "$in_file" ]; then
  echo "The file '$in_file' not exist" >&2
  exit 1
fi
#
addlayersql_py='addlayersql.py'
if [ ! -f "$addlayersql_py" ]; then
  echo "The file '$addlayersql_py' not exist" >&2
  exit 1
fi
#
cat $in_file $addlayersql_py | xclip -selection clipboard
#
name_action=$(echo $in_file | cut -d'_' -f2- | cut -d'.' -f1)
echo "Action '"$name_action"' in clipboard"

