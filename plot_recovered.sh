#!/usr/bin/env bash

country_label="$(tr [A-Z] [a-z] <<< "$1")"
pwd=$(pwd)

gnuplot <<- EOF
  set print "-"

  data_file_name = 'recovered_history.csv'

  time_format = '%m-%d-%y'

  today_date = strftime(time_format, time(0)-18000)

  output_file_relative_path = sprintf('plots/recovered/${country_label} - %s.png', today_date)

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

  set title 'COVID-19 Incidence in ${1} [max. 21 days back]'

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

  days_in_the_future = 2

  start_float = strptime(time_format, start_string)

  end_string = strftime(time_format, strptime(time_format, strftime(time_format, time(0)-18000))+days_in_the_future*86400)

  end_float = strptime(time_format, end_string)

  plot_limit = strftime(time_format, time(0)-1832400)

  first_day = start_float < plot_limit ? start_float : plot_limit

  not_earlier_than_first_day(x) = strptime(time_format, x) < start_float ? NaN : x



  set xrange[first_day:end_float]



  plot \
  data_file_name using (not_earlier_than_first_day(stringcolumn(1))):(column('${country_label}')) w boxes lc rgb 'green' ti 'Recovered', \
  \
  '' using (not_earlier_than_first_day(stringcolumn(1))):(column('${country_label}')):(column('${country_label}')) with labels textcolor rgb 'grey' font ', 7' offset char 0,1 notitle, 


  print("${HOST}".output_file_relative_path)
EOF
