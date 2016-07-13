import requests
import Levenshtein
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pprint import pprint
from monkeylearn import MonkeyLearn
import selenium
from selenium import webdriver
import re
import HTMLParser
from linkedin import linkedin
from bs4 import BeautifulSoup
from bs4 import Comment
import numpy as np
import sys

#count = 0
arr_of_arr = []
total_tries = 1
location_tag = ''
fullName = ''
num = 0

twitter_handles = []

query = 'NAME'
profile_link = "URL"

driver = webdriver.Chrome(executable_path=r"PATH")


def get_twitter_urls(query):
	handle_array = []
	only_handle_array = [] 
	link = 'https://www.googleapis.com/customsearch/v1?key='KEY'&cx='CX'&q=' + query
	r = requests.get(link)
	#"https://www.googleapis.com/customsearch/v1?q=Naren+Patil&cx=008752968299919631116%3Auyoq14caveu&key={AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0}")
	for x in r.json()['items']:
		handle_array.append(x['formattedUrl'])
	for handle_link in handle_array:
		if handle_link.count('/') == 3 and handle_link.startswith('https://twitter.com/') and '=' not in handle_link:
			only_handle_array.append(handle_link.replace('https://twitter.com/',''))
	#printer(only_handle_array)
	pprint(only_handle_array)
	return only_handle_array

def run_pipeline(handle):
    ml = MonkeyLearn('')
    
    data = {
      "twitter_user_name": handle,
      "twitter_access_token_key": '',
      "twitter_consumer_key": '',
      "twitter_consumer_secret": '',
      "twitter_access_token_secret": ''
    }
    
    module_id = 'pi_JJ9JrKvk'
    res = ml.pipelines.run(module_id, data, sandbox=True)
    keyword_array = []
    num = len(res.result['keywords'][0]['keywords'])
    for x in range(0,num):
        keyword_array.append(res.result['keywords'][0]['keywords'][x]['keyword'])
    arr_of_arr.append(keyword_array)

def scrape_linkedin(profile_link):
	driver.get(profile_link)
	html=driver.page_source
	soup=BeautifulSoup(html, "lxml") #specify parser

	name = soup.find('title')
	fullName = name.getText().split("|")[0]

	profile_summary=soup.find('section', { "id" : "summary" })
	try:
		profile_summary = profile_summary.getText()
	except AttributeError:
		profile_summary = ''

	skills_result = soup.find_all(attrs={'class': re.compile(r"^skill$")})
	skills_array = []

	for i in skills_result:
		#pprint(i)
		li = []
		for x in i:
			li.append(str(x))
		#print(li)
		for line in li:
			if "title" in line:
				title_split = line.split("title=\"")
				skills_text = title_split[1].split('"')
				skills_array.append(skills_text[0])
	#pprint(skills_array)

	location_tag = soup.find_all(attrs={'class': re.compile(r"^locality$")})
	#pprint(location_tag)
	span = ""
	for i in location_tag:
		#pprint(i)
		for x in i:
			span = (str(x))
	location_tag = span
	#pprint(location_tag)

	school_array = []

	all_schools = soup.find_all(attrs={'class': re.compile(r"^school$")})
	als = str(all_schools)
	split1 = als.split('ppro_sprof">')
	###pprint(split1)
	for x in split1:
		if x.startswith('<img') or x.startswith('[<li'):
			x = x
		else:
			univ = x.split('</a>')
			school_array.append(univ[0])

	skills_string = ''
	for skills in skills_array:
		skills_string += skills + ' , '

	linkedin_string = skills_string #+ summary
	#pprint(linkedin_string)
	return linkedin_string,location_tag,school_array
		

def linkedin_keyword_extractor(text,location_tag,school_array):
	linkedin_keyword_array = []

	ml = MonkeyLearn('')
	text_list = [text]
	if text_list == ['']:
		text_list = ['none']
	module_id = 'ex_y7BPYzNG'
	res = ml.extractors.extract(module_id, text_list)

	for x in range(0,len(res.result[0])):
		linkedin_keyword_array.append(res.result[0][x]['keyword'])

	for school in school_array:
		linkedin_keyword_array.append(school)
	linkedin_keyword_array.append(location_tag)
	#pprint(linkedin_keyword_array)
	return linkedin_keyword_array

def fuzz_method(linkedin_words, twitter_words):
	counter = 0
	temp_arr = []
	for t in twitter_words:
		for l in linkedin_words:
			temp_arr.append(fuzz.token_sort_ratio(t,l))
			if fuzz.token_sort_ratio(t,l) > 70 and fuzz.token_sort_ratio(t,l) <= 80:
				counter+= 215
			if fuzz.token_sort_ratio(t,l) > 60 and fuzz.token_sort_ratio(t,l) <= 70:
				counter+= 125
			if fuzz.token_sort_ratio(t,l) > 50 and fuzz.token_sort_ratio(t,l) <= 60:
				counter+= 80
			if fuzz.token_sort_ratio(t,l) > 40 and fuzz.token_sort_ratio(t,l) <= 50:
				counter+= 30
			#if fuzz.token_sort_ratio(fullName,query) > 80:
				#counter += 700
	return counter

def runner():
	twitter_handles = get_twitter_urls(query) # twitter_handles is an array
	if len(twitter_handles) == 1:
		pprint('MATCHED twitter handle:' + twitter_handles[0])
		sys.exit('found')
	for handle in twitter_handles:
		run_pipeline(handle)
	#pprint(arr_of_arr)
	linkedin_string,location_tag,school_array = scrape_linkedin(profile_link)
	linkedin_words = linkedin_keyword_extractor(linkedin_string,location_tag,school_array)


	one_runner = []
	total_tries = len(arr_of_arr)
	for user in range(0, len(arr_of_arr)):
		#pprint(twitter_handles[user])
		twitter_words = arr_of_arr[user]
		#pprint(twitter_words)
		#pprint(linkedin_words)
		score = fuzz_method(linkedin_words, twitter_words)
		one_runner.append(score)
		#pprint('-----------------')
	pprint(one_runner)
	return one_runner,twitter_handles

def main():
	output_array = []
	final_array = []
	run_array_1,t1 = runner()
	pprint('1 runner complete ')
	run_array_2,t2 = runner()
	pprint('2 runner complete ')
	run_array_3,twitter_handles = runner()
	pprint('3 runner complete ')

	size = len(run_array_3)/3
	size2 = size*2
	for x in range(0,size):
		output_array.append([run_array_1[x],run_array_2[size + x],run_array_3[size2 + x]])
	for x in output_array:
		final_array.append(sum(x) / float(3))

	altered= final_array[0:3]
	pprint(altered)
	twitter_handles_edit = twitter_handles[0:3]
	pprint(twitter_handles[0:3])
	full_arr = zip([0,1,2],altered)
	pprint(full_arr)

	altered_np = np.asarray(full_arr)

	np_array = np.asarray(altered)
	from scipy import stats
	zscore_arr = stats.zscore(np_array)
	print(zscore_arr)

	#zscore_arr = zip(zscore_arr,twitter_handles[0:3])
	#zscore_sorted = zscore_arr.sort()
	#pprint(zscore_sorted)
	pprint('\n\n\n\n\n')
	if(np.amax(zscore_arr) >= 1):
		x = np.amax(altered_np, axis=1)
		pprint(x[0].astype(np.int))
		pprint('MATCHED twitter handle:' + twitter_handles_edit[x[0].astype(np.int)])
	else:
		pprint('***There is NO twitter handle found***')
	pprint('\n\n\n\n\n')

main()

