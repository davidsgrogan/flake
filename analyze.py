from collections import defaultdict
import math


def GetListOfFlakePairs(list_of_flakes):
  length = len(list_of_flakes)
  list_of_pairs = []
  for i in xrange(length - 1):
    for j in xrange(i + 1, length):
      list_of_pairs.append((list_of_flakes[i], list_of_flakes[j]))


#      print list_of_pairs[-1]
  return list_of_pairs

with open("7_days_scrubbed.csv") as fp:
  test_name_to_count = defaultdict(int)
  pair_to_count_of_cooccurrence = defaultdict(int)
  #  run_to_list_of_tests = defaultdict(list)
  previous_run_id = "dummy"
  number_of_runs = 0
  list_of_tests_flaked_in_current_run = []
  for cnt, line in enumerate(fp):
    array = line.split(",")
    run_id = array[0]
    flaky_test_name = array[1].rstrip()
    #run_to_list_of_tests[run_id].append(flaky_test_name)
    test_name_to_count[flaky_test_name] += 1

    if previous_run_id != run_id:
      number_of_runs += 1
      list_of_pairs = GetListOfFlakePairs(list_of_tests_flaked_in_current_run)
      for pair in list_of_pairs:
        pair_to_count_of_cooccurrence[pair] += 1

      list_of_tests_flaked_in_current_run = []
      previous_run_id = run_id

    list_of_tests_flaked_in_current_run.append(flaky_test_name)

pair_to_correlation_coeff = {}
for pair, count in pair_to_count_of_cooccurrence.iteritems():
  float_number_of_runs = float(number_of_runs)
  e_xy = count / float_number_of_runs
  e_x = test_name_to_count[pair[0]] / float_number_of_runs
  assert e_x > 0, "got %f for %s with count of %d" % (
      e_x, pair[0], test_name_to_count[pair[0]])
  e_y = test_name_to_count[pair[1]] / float_number_of_runs
  assert e_y > 0
  stdev_x = math.sqrt(e_x * (1 - e_x))
  stdev_y = math.sqrt(e_y * (1 - e_y))
  correlation_coeff = (e_xy - e_x * e_y) / (stdev_x * stdev_y)
  assert correlation_coeff >= -1.01
  assert correlation_coeff <= 1.01, correlation_coeff
  print correlation_coeff, pair
