# linkedin_to_twitter
keyword-matcher.py uses a publicly found LinkedIn URL of a user's profile and that user's full name (which can be taken directly from the LinkedIn URL if need be) and scrapes the LinkedIn profile for the users full name, location tag, summary, skills, and education. It properly formats these attributes into a string. 

Using MonkeyLearn ( Machine Learning API to automate text classification) and its Keyword Extraction module, the LinkedIn string is condensed down to 10 or so keywords. Using Google customsearch API (I've created 2 custom search engines which respectively search twitter.com and linkedin.com) and Twitter Search API, I query with the users full name and find the intersection of the responses. The responses are twitter handles which are then fed to MonkeyLearn's Twitter Classifier, which analyzes tweets and returns a set of keywords the handles are interested in. Using fuzzywuzzy, which is a python library that uses Levenshtein Distance to help calculate differences between sequences, I match each handles keywords against the LinkedIn keywords from before, giving points based on the number of occurences of scores greater than 50,60,70,and 80 (also add points for matching locations and full_names). Thus, the program rewards points to Twitter handles with similar 'interests' as the LinkedIn profile as identified by the keyword extractions as well as significant point additions to profiles with the same name and general location. 

If the top-scoring Twitter handle is far enough ahead of its competing handles, it is returned as the matching profile. If not, keyword-matcher.py says that there is no twitter handle for the user. 

Currently, the program works best with LinkedIn and Twitter profiles that have a consequential amount of content. If either is lacking, the matching is not as strong, and can lead to incorrect results. Based on preliminary testing, I'd say it works 80% of the time, with its largest source of error as false positives.

The program is released under the MIT License
