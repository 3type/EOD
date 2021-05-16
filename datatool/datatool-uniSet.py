# import json
import pickle
import gzip

from json_file import load_json
from json_file import dump_json

uniList_GB2312 = load_json('GB2312.json')
uniList_GB2312.sort()

uniList_Big5 = load_json('Big5.json')
uniList_Big5.sort()

uniList_Hanyi9169 = load_json('Hanyi9619.json')
uniList_Hanyi9169.sort()

charSetDict = {
    'GB2312': uniList_GB2312,
	'Big5': uniList_Big5,
	'Hanyi9169': uniList_Hanyi9169
}

# with open('./output/charSetDict.pickle', 'wb') as outfile:
#     pickle.dump(charSetDict, outfile)
#     print('### pickle Done')

with gzip.open('./output/charSetDict.pdata', 'w') as outfile:
    outfile.write(pickle.dumps(charSetDict))
    print('### pickle/gzip Done')

# with open('./output/tmp/charSetDict.json', 'w') as outfile:
#     json.dump(charSetDict, outfile)
#     print('### charSetDict json Done')
