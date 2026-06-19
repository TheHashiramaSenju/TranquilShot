#!/bin/bash

CONDIR="${CONDIR:-my_project}"

if [ ! -d "$CONDIR" ] || [ -z "$(ls -A "$CONDIR" 2>/dev/null)" ]; then
    
    echo "Directory ($CONDIR) is empty or missing. Initializing project layout..."
    
    mkdir -p "$CONDIR"/{hardware,utils,models}

    touch "$CONDIR"/{main.py,config.py,requirements.txt}
    touch "$CONDIR"/hardware/{__init__.py,camera_tpu.py,tof_sensors.py,pixhawk_link.py}
    touch "$CONDIR"/utils/{__init__.py,math_helpers.py,logger.py}
    touch "$CONDIR"/models/{target_edgetpu.tflite,labels.txt}

    FILE_COUNT=$(find "$CONDIR" -type f | wc -l)
    echo "Project structure initialized. Total files created: $FILE_COUNT"
 
else
   
    echo "Aborting layout creation. Files already present in directory ($CONDIR):"
    ls -A "$CONDIR"
fi

