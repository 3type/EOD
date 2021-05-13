# encoding: utf-8

################################################################################
#
# IDS dataset tool
#
################################################################################

import csv
import re
# import json
import gzip
import pickle


# TSVs of ids data
# CHISE ids project: https://gitlab.chise.org/CHISE/ids
idsTSVList = ['./dataset/ids/IDS-UCS-Basic.txt',
		'./dataset/ids/IDS-UCS-Ext-A.txt']

# TSVs of your ids patch to override
# !!! Please follow the CHISE style format
idsPatchList = ['./dataset/custom/IDS-UCS-Basic-Patch.txt',
		'./dataset/custom/IDS-UCS-Ext-A-Patch.txt']

# TSVs of Unihan data
# Unihan project: http://www.unicode.org/reports/tr38
unihanTSVList = ['./dataset/Unihan/Unihan_IRGSources.txt']


def readTSVs(tsvList):
	tsvData = []
	for tsvFile in tsvList:
		with open(tsvFile, 'r') as tsv_in:
			tsvReader = csv.reader(tsv_in, delimiter='\t')
			tsvLabels = tsvReader.__next__()
			for record in tsvReader:
				tsvData.append(record)
	return tsvData

idsTSVData = readTSVs(idsTSVList+idsPatchList)

unihanTSVData = readTSVs(unihanTSVList)


# unihanTSVData = []
# for unihanTSV in unihanTSVList:
# 	with open(unihanTSV, 'r') as tsv_in:
# 		tsvReader = csv.reader(tsv_in, delimiter='\t')
# 		tsvLabels = tsvReader.__next__()
# 		for record in tsvReader:
# 			unihanTSVData.append(record)

unihanDict = {}
for lineList in unihanTSVData:
	if len(lineList)>=3 and lineList[1] == 'kTotalStrokes':
		xUni = lineList[0][2:]
		xTotalStrokes = int(lineList[2].partition(' ')[0])
		unihanDict[xUni] = {'totalStrokes' : xTotalStrokes}


# Package the idsDict
# 	idsDict[xUni] = {'zi': xZi, 'formula': formulaList, 'totalStrokes': totalStrokes}
idsDict = {}

def checkIt(listXY):
	if len(listXY) == 1:
		return 1
	
	if str(listXY[0]) in '⿲⿳':
		for x in listXY[1:4]:
			if str(x) in '⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻⿲⿳':
				return 0
		return 4

	if str(listXY[0]) in '⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻':
		for x in listXY[1:3]:
			if str(x) in '⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻⿲⿳':
				return 0
		return 3

	return 0

''' 
Cut fromula String into List

Input: '⿳⿰巳巳一&GT-K00059;'
Output: ['⿳','⿰','巳','巳','一','GT-K00059']

	[^\u0000-\u007f] >>> NOT Basic Latin Character
	(?<=&).+?(?=;) >>> String surrounded by '&' and ';'

'''
pParts = re.compile(r'[^\u0000-\u007f]|(?<=&).+?(?=;)')

for x in idsTSVData:
	xUni = x[0][2:]
	xZi = x[1]
	formulaRAW = x[2]

	formulaList = re.findall(pParts, formulaRAW)

	# IDS formula parser
	iX = 0
	while checkIt(formulaList) == 0:
		if checkIt(formulaList[iX:iX+4]) == 0:
			iX += 1
		elif checkIt(formulaList[iX:iX+4]) == 3:
			formulaList = formulaList[:iX] + [formulaList[iX:iX+3]] + formulaList[iX+3:]
			iX = 0
		elif checkIt(formulaList[iX:iX+4]) == 4:
			formulaList = formulaList[:iX] + [formulaList[iX:iX+4]] + formulaList[iX+4:]
			iX = 0

	if formulaList == [xZi]:
		formulaList = ['○', xZi, xZi]

	totalStrokes = unihanDict.get(xUni, {'totalStrokes': 0}).get('totalStrokes')

	idsDict[xUni] = {'zi': xZi, 'formula': formulaList, 'totalStrokes': totalStrokes}

print('### idsDict{} Ready')

# Checking point with buggy formulas
# ['⿳', '彑', ['⿰', '米', '糸'], '廾']
# ['⿳', '𰀉', ['⿱', '冖', 'GT-K00059'], ['⿱', '𠀎', 'CDP-8B67']]
# ['⿰', '止', '?']
print('Checking the Result:')
print('idsDict[''5F5D'']---->',idsDict['5F5D'])
print('idsDict[''56A2'']---->',idsDict['56A2'])
print('idsDict[''3C50'']---->',idsDict['3C50'])

# Export the data as file

# with open('./output/idsDict.json', 'w') as outfile: 
#     json.dump(idsDict, outfile)
#     print('### idsDict{} json Done')

# with open('.output/idsDict.pickle', 'wb') as outfile:
#     pickle.dump(idsDict, outfile)
#     print('### pickle Done')

with gzip.open('./output/idsDict.pdata', 'w') as outfile: 
    outfile.write(pickle.dumps(idsDict))
    print('### idsDict{} pickle+gzip Done')

print('##### All Done')