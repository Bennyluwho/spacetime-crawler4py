import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict


#Q1: not exactly sure if it's revisiting the same page, but if so, probably use unique pages?
unique_pages = set()

#Q2, idea: probably use tokens :p
longest_page = ("", 0)

#Q3:
word_counter = defaultdict(int) # Counter()

#Q4?

# cannot use same exact tokenizer from assignment 1 because of apostrophes in STOPWORDS
STOPWORDS = {"a", "about", "above", "after", "again", "against",
"all", "am","an","and","any","are","aren't","as","at","be","because","been",
"before","being","below","between","both","but","by","can't","cannot",
"could","couldn't","did","didn't","do","does","doesn't","don't","down","during",
"each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having",
"he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself",
"his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it",
"it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor",
"not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own",
"same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that",
"that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll",
"they're","they've","this","those","through","to","too","under","until","up","very","was",
"wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's",
"which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","your","yours","yourself","yourselves"}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = set()

    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, "lxml")

        #Tokenize, update longest page, unique pages, and word_counter
        #TODO: Unique pages
        global longest_page
        global word_counter
        global unique_pages

        # Update unique pages
        # De-fragment
        fragment = url.rfind("#")
        if fragment != -1:
            url = url[:fragment]
        unique_pages.add(url)

        # Update word_counter
        token_amt = 0
        for word in soup.find_all('b'):
            word = word.lower() # lowercase
            if word not in STOPWORDS:
                word_counter[word] += 1
                token_amt += 1

        if longest_page[1] < token_amt: # Update longest page
            longest_page = (url, token_amt)

        for anchor in soup.find_all('a', href = True):
            href = anchor['href']
            #normalize urls
            finished_url = href

            # De-fragment ("defragment the URLs, i.e. remove the fragment part.")
            anchor_fragment = url.rfind("#")
            if anchor_fragment != -1:
                finished_url = finished_url[:anchor_fragment]

            links.add(finished_url)

    return links

def is_valid(url) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    #TODO: crawler traps (discord thread in #resources), notable: calendar, inf traps, 
    # Partly done?
    #TODO: Crawl all pages with high textual information content, so maybe decide validity based on token amount of a page?
    #TODO: Detect and avoid sets of similar pages with no information
    #TODO: Detect and avoid dead URLs that return a 200 status but no data >>>D: Dead URL (also known as a soft 404) check
    #TODO: Detect and avoid crawling very large files, especially if they have low information value

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        wanted_file_ext = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

        valid_domain = bool(re.match(r".*ics.uci.edu*.|"
                                    r".*cs.uci.edu*.|"
                                    r".*informatics.uci.edu*.|"
                                    r".*stat.uci.edu*.", parsed.netloc.lower()))
    
        # Trap detection
        # Apparently, calendars (event[s]) are a well known ics trap.
        known_traps = bool(not re.match(r".*/events/.*|"
                                    r".*/events.*|"
                                    r".*/event/.*|"
                                    r".*/event.*|", parsed.path.lower()))

        return valid_domain & wanted_file_ext & known_traps

            
        


    except TypeError:
        print ("TypeError for ", parsed)
        raise
