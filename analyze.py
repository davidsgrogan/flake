from collections import defaultdict
import math
from pprint import pprint

# TODO(dgrogan): add argv support for:
# input file name
# output histogram or correlations
# infra/harness failure cutoff


def GetListOfFlakePairs(list_of_flakes):
  # Returns list of size combin(N, 2) where N is number of flakes in this run.
  length = len(list_of_flakes)
  list_of_pairs = []
  for i in xrange(length - 1):
    for j in xrange(i + 1, length):
      list_of_pairs.append((list_of_flakes[i], list_of_flakes[j]))
  return list_of_pairs


def ParseLine(line):
  array = line.split(",")
  run_id = array[0]
  flaky_test_name = array[1].rstrip()
  return (run_id, flaky_test_name)


# Collect metadata and transform the real data.
with open("interactive_ui_tests_365_days.csv") as fp:
  test_name_to_count = defaultdict(int)
  pair_to_count_of_cooccurrence = defaultdict(int)
  previous_run_id = "dummy"
  number_of_runs = 0
  list_of_tests_flaked_in_current_run = []
  histogram_runs_per_flake_count = defaultdict(int)
  for cnt, line in enumerate(fp):
    (run_id, flaky_test_name) = ParseLine(line)
    test_name_to_count[flaky_test_name] += 1

    if previous_run_id != run_id:
      # TODO: Assert first occurrence of run_id?
      number_of_runs += 1
      num_current_flakes = len(list_of_tests_flaked_in_current_run)
      assert (previous_run_id == "dummy") == (
          num_current_flakes == 0), "%s %d" % (previous_run_id,
                                               num_current_flakes)
      # >6 seems (via eyeballing the histogram) to indicate an infra/harness
      # failure for interactive_ui_tests.
      if num_current_flakes > 0 and num_current_flakes <= 6:
        histogram_runs_per_flake_count[len(
            list_of_tests_flaked_in_current_run)] += 1
        # Sort to ensure pairs aren't logged differently in different runs, e.g.
        # (a,b) in run 1 and (b,a) in run 2
        list_of_tests_flaked_in_current_run.sort()
        list_of_pairs = GetListOfFlakePairs(list_of_tests_flaked_in_current_run)
        for pair in list_of_pairs:
          if pair[0] == "WebViewBrowserPluginInteractiveTest.EnsureFocusSynced" and pair[1] == "WebViewInteractiveTests/WebViewPointerLockInteractiveTest.PointerLock_PointerLockLostWithFocus/0":
            print previous_run_id
          pair_to_count_of_cooccurrence[pair] += 1

      list_of_tests_flaked_in_current_run = []
      previous_run_id = run_id

    list_of_tests_flaked_in_current_run.append(flaky_test_name)

# The actual math part is below.
pair_to_correlation_coeff = {}  # remove?
for pair, cooccurrence_count in pair_to_count_of_cooccurrence.iteritems():
  float_number_of_runs = float(number_of_runs)
  e_xy = cooccurrence_count / float_number_of_runs
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
#  print cooccurrence_count, test_name_to_count[pair[0]], test_name_to_count[
#      pair[1]], correlation_coeff, pair
#pprint(dict(histogram_runs_per_flake_count))
