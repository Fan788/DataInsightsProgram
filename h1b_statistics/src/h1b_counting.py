import argparse
import csv
import math
import os
import sys
from collections import Counter
from operator import itemgetter


parser = argparse.ArgumentParser(description='Process input/output.')
parser.add_argument('-i', dest='input_path', metavar=('a.csv',), type=str, nargs=1,
                    help='one input path')
parser.add_argument('-o', dest='output_paths', metavar=('b.csv', 'c.csv'), type=str, nargs=2, help='two output paths. 1st for occupation, second for state.')


def ReadData(filename, fields_to_count):
	"""Read data from filename and generate Counters for each fields_to_count.

	Args:
		filename - path of file to read.
		fields_to_count - list of field names to count.

	Returns:
		(counters, num_rows)
		counters - {field_name: Counter instant}
		num_rows - total number of lines
	"""
	counters = dict()
	for field_name in fields_to_count:
		counters[field_name] = Counter()
	num_rows = 0
	with open(filename) as csvfile:
	     reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
	     for row_as_dict in reader:
	     	num_rows += 1
	     	if row_as_dict['CASE_STATUS'] != 'CERTIFIED':
	     		continue
	     		# filter out the CASE_STATUS which are not CERTIFIED
	     		
	     	for field_name in fields_to_count:
	     		# Get the Counter of field_name as cur_counter
	     		cur_counter = counters[field_name]
	     		# Increment for the value of field_name in this row.
	     		cur_counter[row_as_dict[field_name]] += 1
	return counters, num_rows


def WriteData(filename, name_field, element_list):
	""" Write element_list to a file in filename.

	The 3rd value in each tuple of element_list is a ratio. The writer converts it to a perceptage with 1 digit after decimal point.

	Args:
		filename - path of output file to write.
		name_field - 1st field in csv file corresponding to the first element in element_list.
		element_list - [(name(str), count(int), ratio(float)), ...]
	"""
	fieldnames = [name_field, 'NUMBER_CERTIFIED_APPLICATIONS', 'PERCENTAGE']
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quotechar='"')
		writer.writeheader()
		for name, cnt, ratio in element_list:
			formatted_elem = {
				name_field: name,
				'NUMBER_CERTIFIED_APPLICATIONS': cnt,
				'PERCENTAGE': '{}%'.format(round(ratio * 100, ndigits=1))}
			writer.writerow(formatted_elem)


def GetTopKElements(counter, k, total_num):
	""" Find top k elements from input counter.
	Args:
		counter - a Counter instance
		k - int, the k largest elements
		total_num - int, a number used to calculate percetage of count, as count / total_num.

	Returns:
		A list of tuple of name(str), count(int), ratio(float) of count w.r.t total_num.
	"""
	# get the items list like (software e, 3) etc
	name_and_cnt_list = counter.items()
	# Sort by name in ascending order.
	name_and_cnt_list.sort(key=itemgetter(0), reverse=False)
	# Sort by count in descending order. so it is sorted by the cnt first then name
	name_and_cnt_list.sort(key=itemgetter(1), reverse=True)
	# Return the first K elements
	return [(name, cnt, float(cnt) / total_num) for name, cnt in name_and_cnt_list[:k]]


def main():
	args = parser.parse_args(sys.argv[1:])

	# Parse input and output paths from commandline arguments.
	input_filename = args.input_path[0]
	top_occupation_filename = args.output_paths[0]
	top_state_filename = args.output_paths[1]

	# Create {field_name: Counter()} from input file.
	all_counters, total_num_applications = ReadData(input_filename, ['SOC_NAME', 'WORKSITE_STATE'])

	job_counter = all_counters['SOC_NAME']
	state_counter = all_counters['WORKSITE_STATE']

	# Sort the elements in each counter and return the top 10 with count and ratio.
	top_10_jobs = GetTopKElements(job_counter, 10, total_num_applications)
	top_10_states = GetTopKElements(state_counter, 10, total_num_applications)

	# Write out.
	WriteData(top_occupation_filename, 'TOP_OCCUPATIONS', top_10_jobs)
	WriteData(top_state_filename, 'TOP_STATES', top_10_states)


if __name__ == "__main__":
	main()
