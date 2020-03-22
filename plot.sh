#!/bin/bash

countryLabel="$(tr [A-Z] [a-z] <<< "$1")"
daysAgo=${2}
addendum=""
pwd=$(pwd)
if [ "$3" == "False" ]; then addendum="(not updated yet)"; fi
if [ ! $daysAgo -eq 0 ]; then addendum="(from ${daysAgo} days ago)"; fi

gnuplot <<- EOF
  datafileName = 'history.csv'

  timeFmt = '%m-%d-%y'

  todayDate = strftime(timeFmt, time(0)-18000)

  set output sprintf('${pwd}/plot/plot ${countryLabel} ${daysAgo} - %s.png', todayDate)

  set datafile separator ','

  set grid

  set border lw 1 lc rgb 'grey'

  set xtics textcolor rgb 'grey' font ', 8'

  set ytics textcolor rgb 'grey'

  set key textcolor rgb 'grey'

  set title textcolor rgb 'grey'

  set size ratio 0.45

  set title 'COVID-19 Incidence in ${1} ${addendum}'

  set terminal pngcairo enhanced background rgb 'black' size 720, 640

  set ylabel '' tc rgb 'grey' #'Confirmed cases'

  set xlabel '' tc rgb 'grey' #'Date'

  set style fill solid 0.3

  set key left

  set style fill solid 0.3

  set offsets graph 0.1, 2, 20, 0

  set grid xtics, ytics

  set key top left

  set timefmt '%m/%d/%y'

  set xdata time

  set format x '%b %d'# time



  set table 'dummy'
    plot datafileName using (startStr=stringcolumn('${countryLabel}')):185 every ::0::1 w table
  unset table



  timeFmt = '%m/%d/%y'

  daysInTheFuture = 4

  todayFt = strptime(timeFmt, strftime(timeFmt, time(0)-18000)) - $daysAgo*86400

  todayStr = strftime(timeFmt, todayFt)

  yesterdayFt = todayFt - 1*86400

  yesterdayStr = strftime(timeFmt, todayFt-1*86400)

  startFt = strptime(timeFmt, startStr)

  endStr = strftime(timeFmt, strptime(timeFmt, strftime(timeFmt, time(0)-18000))+daysInTheFuture*86400)

  endFt = strptime(timeFmt, endStr)

  q = (todayFt - startFt)/86400/20

  N = q <= 1.0 ? 1 : ceil(q)

  delta = int((endFt - todayFt)/86400) - 1

  days_plotted = $daysAgo <= q*20 ? 1 : int(q*20/$daysAgo)

  not_greater_than_today(x) = todayFt >= strptime(timeFmt, x) ? x : NaN

  days(x) = (strptime(timeFmt, x)-startFt)/86400.0

  is_in_range(x) = startFt == strptime(timeFmt, x) || (strptime(timeFmt, x) <= strptime(timeFmt, strftime(timeFmt, time(0)-18000)) && (ceil(days(x))%N == 0)) ? x : NaN

  is_zero(x) = x == 0 ? NaN : x



  a = 1

  b = 1e-6

  f(x) = a*exp(b*int((x-startFt)/86400+1))

  fit [startFt:todayFt] f(x) datafileName using 185:'${countryLabel}' via a,b

  cases_at(x) = int(f(todayFt + (x)*86400))

  date_after(x) = strftime(timeFmt, todayFt + x*86400)

  array A[delta]

  array B[delta]

  do for [i=1:delta] {
    A[i] = date_after(i)
    B[i] = cases_at(i)
  }



  set label 1 at graph 0.237, graph 0.793 'Expected' tc rgb 'orange' front
  set label 2 at graph 0.162, graph 0.725 sprintf('Doubling every   %.2f days',(log(2)/b)) tc rgb 'grey' front



  set xrange[startFt:endFt]

  set samples (endFt - startFt)/86400.0 + 1



  plot \
  f(x) w l lc rgb 'red' ti sprintf('f(x) = %0.4fe^{(%0.4fx)}', a, b), \
  \
  datafileName using (is_in_range(stringcolumn(185))):'${countryLabel}' w lp pt 7 lc rgb 'blue' ti 'Confirmed cases', \
  \
  '' using (is_in_range(stringcolumn(185))):(is_zero(column('${countryLabel}'))):'${countryLabel}' with labels textcolor rgb 'grey' font ', 8' offset char 0,1.3 notitle, \
  \
  todayFt < x && x < endFt ? f(x) : 1/0 w p pt 7 lc rgb 'yellow' ti ' ', \
  \
  B using (A[\$1]):(B[\$1]):(sprintf('%.0f', B[\$1])) every days_plotted with labels textcolor rgb 'orange' font ', 8' offset char 0,2 notitle, \
  \
  '' using 185:'${countryLabel}' ti '    ' lc rgb '#00000000' ps 0
EOF
