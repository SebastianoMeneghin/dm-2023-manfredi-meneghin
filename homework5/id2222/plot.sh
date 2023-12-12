#!/bin/bash

#check for installation of parallel-rsync

#if [ "$#" -ne 1 ] ; then
#	echo "Data file not supplied."
#	echo "Usage ./plot {data-file.txt}"
#	exit
#fi

#gnuplot -e "filename='$1'" graph.gnuplot

#xdg-open graph.png

#!/bin/bash

#check for installation of parallel-rsync

if [ "$#" -lt 1 ] ; then
	echo "Data file not supplied."
	echo "Usage ./plot {data-file.txt}"
	exit
fi

gnuplot -e "filename='$1'" graph.gnuplot

if [ "$#" -lt 2 ] ; then
  xdg-open graph.png
else
  echo "Creating graph at $2"
  mv graph.png $2
fi
