# if you want to validate data from a CSV file, you have to first construct
# a CSV reader using the standard Python `csv` module, specifying the appropriate
# dialect, and then pass the CSV reader as the source of data to either the
# `CSVValidator.validate` or the `CSVValidator.ivalidate` method

import argparse
import os
import sys
import csv
from csvvalidator import *
import re

def create_validator():
	field_names = (
					'IP',
					'DNS',
					'NetBIOS',
					'OS',
					'IP Status',
					'QID',
					'Title',
					'Type',
					'Severity',
					'Port',
					'Protocol',
					'FQDN',
					'SSL',
					'CVE ID',
					'Vendor Reference',
					'Bugtraq ID',
					'Threat',
					'Impact',
					'Solution',
					'Exploitability',
					'Associated Malware',
					'Results',
					'PCI Vuln',
					'Instance',
					'Category'
					)
	validator = CSVValidator(field_names)

	# header check
	validator.add_header_check('HEADER_CHECK_FAILED', 'Incorrect fields in header! ')

	# record length check, for every row
	validator.add_record_length_check('RECORD_LENGTH_CHECK_FAILED', 'The length of the record is incorrect!')

	# IP value check: '\d+\.\d+\.\d+\.\d+', with range 1~255
	#ip_pattern = '^[1-2]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]\.[1-2]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]\.[1-2]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]\.[1-2]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]$'
	ip_pattern = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
	validator.add_value_check('IP', match_pattern(ip_pattern), 'IP_VALUE_CHECK_FAILED', 'IP value is not correct!')
	
	# CVE ID value check
	
	# Severity value check
	severity_pattern = '^\s*$|^[1-9]$|^10$'
	validator.add_value_check('Severity', match_pattern(severity_pattern), 'SEVERITY_VALUE_CHECK_FAILED', 'Severity value is not correct!')

	return validator

max_file_size = 52428800 # 50MB

def validateCSV(inputFile):
	validateMessage = "Validate %s " % inputFile.name
	validateCode = 0

	# check file suffix
	if not inputFile.name.endswith('.csv'):
		validateMessage += 'failed!\n\nError: %s is NOT a csv file!\n' % inputFile.name
		validateCode = 1
		return validateCode, validateMessage

	# file size check
	if inputFile.size > max_file_size:
		validateMessage += 'failed!\n\nError: %s size too big for processing!\nFile size limit: %dMB.\n' % (inputFile, max_file_size / (1024 * 1024))
		validateCode = 1
		return validateCode, validateMessage

	inputData = csv.reader(inputFile)
	backupData = csv.reader(inputFile)
	ignoredLines = 0
	counter = 0;
	headerFlag = False;

	for row in inputData:
		if row:
			if row[0] == "IP":
				ignoredLines = counter
				headerFlag = True
		counter += 1;

	if ignoredLines == 0 and counter == 0:
		validateMessage += "failed!\n\nError: %s is empty!\n" % inputFile
		validateCode = 1
		return validateCode, validateMessage

	if not headerFlag:
		validateMessage += "failed!\n\nError: %s does not have a header with the 1st field as 'IP'!" % inputFile
		validateCode = 1
		return validateCode, validateMessage

	if ignoredLines == counter - 1:
		validateMessage += "failed!\n\nError: %s has no useful data!" % inputFile
		validateCode = 1
		return validateCode, validateMessage		

	# create a validator
	validator = create_validator()

	# validate the data from the csv reader
	# ignore lines (rows) at the beginning of the data
	problems = validator.validate(backupData, ignore_lines=ignoredLines) 
 
	if problems:
		validateMessage += "failed!\n\n Errors:"
		validateMessage += writeProblemsToString(problems)
		validateCode = 1
	
	return validateCode, validateMessage

def writeProblemsToString(problems, summarize=False, limit=0):
    """
    Write problems to a string.
    """
    reportString = ""
    counts = dict() # store problem counts per problem code
    total = 0
    for i, p in enumerate(problems):
        if limit and i >= limit:
            break # bail out
        total += 1
        code = p['code']
        if code in counts:
            counts[code] += 1
        else:
            counts[code] = 1
        if 'code' in p and p['code']:
        	if 'row' in p and 'message' in p:
        		reportString += "\nRow %s: " % p['row']
        	if p['code'] == 'HEADER_CHECK_FAILED':
        		if 'missing' in p and p['missing']:
        			reportString += "Missing fileds"
        			for cur in p['missing']:
        				reportString += " \'%s\'" % cur
        			reportString += " in header! "
        		if 'unexpected' in p and p['unexpected']:
        			reportString += "Unexpected fields"
        			for cur in p['unexpected']:
        				reportString += " \'%s\'" % cur
        			reportString += " in header!"	
          	if p['code'] == 'RECORD_LENGTH_CHECK_FAILED':
          			if 'length' in p and p['length']:
        				reportString += "Record length is %s, expected to be 25!" % p['length']
          	if p['code'] == 'IP_VALUE_CHECK_FAILED':
          			if 'value' in p:
          				if p['value']:
        					reportString += "Invalid IP value \'%s\', expected to be in format xxx.xxx.xxx.xxx and \'xxx\' between 0 and 255!" % p['value']			
        				else:
        					reportString += "Empty IP value! Not allowed!"
          	if p['code'] == 'SEVERITY_VALUE_CHECK_FAILED':
          			if 'value' in p and p['value']:
        					reportString += "Invalid severity value \'%s\', expected to be between 1 and 10 or empty!" % p['value']
    reportString += "\n\nFound %s problem in total.\n" % total
    return reportString