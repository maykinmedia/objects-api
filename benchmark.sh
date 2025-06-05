#!/bin/bash

PROCESSES=${PROCESSES:-100}

echo "Using $PROCESSES processes..."

for (( idProcess=0; idProcess<PROCESSES; idProcess++ ));
do
    OUTPUT_FORMAT="Elapsed time: %{time_total}s\nProcess: $idProcess\n";

    (
        curl \
            --get \
            --header 'Authorization: Token secret' \
            --data 'pageSize=1000' \
            --data 'type=http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662' \
            --data 'data_attrs=kiemjaar__exact__1234' \
            --data 'ordering=-record__data__contactmoment__datumContact' \
            --write-out "$OUTPUT_FORMAT" \
            --output /dev/null \
            --silent \
            http://localhost:8000/api/v2/objects;
    ) &
done

wait
