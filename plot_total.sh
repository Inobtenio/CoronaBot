#!/usr/bin/env bash

country_label="$(tr [A-Z] [a-z] <<< "$1")"
days_ago=${2}
pwd=$(pwd)

gnuplot <<- EOF
  set print "-"

  data_file_name = 'total_history.csv'

  time_format = '%m-%d-%y'

  today_date = strftime(time_format, time(0)-18000)

  output_file_relative_path = sprintf('plots/total/${country_label} ${days_ago} - %s.png', today_date)

  output_file_name = sprintf('${pwd}/%s', output_file_relative_path)

  set output output_file_name

  set datafile separator ','

  set grid

  set border lw 1 lc rgb 'grey'

  set xtics textcolor rgb 'grey' font ', 8'

  set ytics textcolor rgb 'grey'

  set key textcolor rgb 'grey'

  set title textcolor rgb 'grey'

  set size ratio 0.45

  set title 'COVID-19 Incidence in ${1}'

  set terminal pngcairo enhanced background rgb 'black' size 720, 640

  set ylabel '' tc rgb 'grey'

  set xlabel '' tc rgb 'grey'

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
    plot data_file_name using (start_string=stringcolumn('${country_label}')):1 every ::0::1 w table
  unset table



  time_format = '%m/%d/%y'

  days_in_the_future = 4

  today_float = strptime(time_format, strftime(time_format, time(0)-18000)) - $days_ago*86400

  today_string = strftime(time_format, today_float)

  yesterday_float = today_float - 1*86400

  yesterday_string = strftime(time_format, today_float-1*86400)

  start_float = strptime(time_format, start_string)

  end_string = strftime(time_format, strptime(time_format, strftime(time_format, time(0)-18000))+days_in_the_future*86400)

  end_float = strptime(time_format, end_string)

  q = (today_float - start_float)/86400/21

  N = q <= 1.0 ? 1 : ceil(q)

  delta = int((end_float - today_float)/86400) - 1

  days_plotted = $days_ago <= q*20 ? 1 : int(q*20/$days_ago)

  not_greater_than_today(x) = today_float >= strptime(time_format, x) ? x : NaN

  days(x) = (strptime(time_format, x)-start_float)/86400.0

  is_in_range(x) = start_float == strptime(time_format, x) || (strptime(time_format, x) == strptime(time_format, strftime(time_format, time(0)-18000)) || (ceil(days(x))%N == 0)) ? x : NaN

  is_zero(x) = x == 0 ? NaN : x



  a = 1

  b = 1e-6

  f(x) = a*exp(b*int((x-start_float)/86400+1))

  fit [start_float:today_float] f(x) data_file_name using 1:'${country_label}' via a,b

  cases_at(x) = int(f(today_float + (x)*86400))

  date_after(x) = strftime(time_format, today_float + x*86400)

  array A[delta]

  array B[delta]

  do for [i=1:delta] {
    A[i] = date_after(i)
    B[i] = cases_at(i)
  }



  set label 1 at graph 0.237, graph 0.793 'Expected' tc rgb 'orange' front

  set label 2 at graph 0.162, graph 0.725 sprintf('Doubling every   %.2f days',(log(2)/b)) tc rgb 'grey' front



  set xrange[start_float:end_float]

  set samples (end_float - start_float)/86400.0 + 1



  plot \
  f(x) w l lc rgb 'red' ti sprintf('f(x) = %0.4fe^{(%0.4fx)}', a, b), \
  \
  data_file_name using (is_in_range(stringcolumn(1))):'${country_label}' w lp pt 7 lc rgb 'blue' ti 'Total confirmed cases', \
  \
  '' using (is_in_range(stringcolumn(1))):(is_zero(column('${country_label}'))):'${country_label}' with labels textcolor rgb 'grey' font ', 7' offset char 0,0.8 notitle, \
  \
  today_float < x && x < end_float ? f(x) : 1/0 w p pt 7 lc rgb 'yellow' ti ' ', \
  \
  B using (A[\$1]):(B[\$1]):(sprintf('%.0f', B[\$1])) every days_plotted with labels textcolor rgb 'orange' font ', 8' offset char 0,2 notitle, \
  \
  '' using 1:'${country_label}' ti '    ' lc rgb '#00000000' ps 0


  print("${HOST}".output_file_relative_path)
EOF
