import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import defaultdict
from tldextract import extract

#import hashlib

#EC1A: EXACT webpage similarity detection 
#seen_hashes = set()

# NEAR-similar set
threegrams = set()

#TODO: EC1B: implement near webpage similarity detection

#Q1:
unique_pages = set()

#Q2, idea: probably use tokens :p
longest_page = ("", 0)

#Q3:
word_counter = defaultdict(int) # Counter()


#Q4: (in write_crawl_report)

def write_crawl_report():
    q1 = len(unique_pages)
    q2_url, q2_length = longest_page
    q3 = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)[:50]

    #Increment number after each submission
    with open("Submission1.txt", "w", encoding="utf-8", errors='ignore') as stats:
        stats.write(f"Q1: {q1} unique pages\n\n")
        stats.write(f"Q2: Longest page: {q2_url} with {q2_length} words\n\n")
        stats.write(f"Top 50 most common words: \n\n")
        for word, count in q3:
            stats.write(f"{word}: {count}\n")

        #q4
        # server is down so still has to be tested
        stats.write(f"\nSubdomains: \n\n")
        subdomain_counts = defaultdict(int)
        for u in unique_pages:
            # extract splits the url into subdomain, domain, ect.
            # Just to be safe I urlparsed each url to pass in just the domain, but this is probably unnecessary
            ext = extract(urlparse(u).netloc)
            if ext.domain == "uci": # Check domain is uci just in case
                subdomain_counts[ext.subdomain] += 1
        subdomains = sorted(list(subdomain_counts.items()), key=lambda x:x[0])
        for subd, amt in subdomains:
            stats.write(f"{subd}.uci.edu, {amt}\n")

def similarity(a: list, b: list):
    if max(len(a), len(b)) == 0:
        return 0
    t1, t2 = list(a), list(b)
    t1.sort()
    t2.sort()

    i, j = 0, 0
    t1len, t2len = len(t1), len(t2)

    count = 0

    while i < t1len and j < t2len:
        if t1[i] == t2[j]:
            count += 1
            i += 1
            j += 1
        elif t1[i] < t2[j]:
            i += 1
        elif t1[i] > t2[j]:
            j += 1

    return count / max(len(a), len(b))

def near_similar(text: list, index: set):
    # Adds to the set inded if the text is similar to an existing ngram, otherwise does nothing. 
    N = 3
    THRESH = 0.9 # If over 0.9 similarity, disregard
    ngrams = set()
    if len(text) >= N:
        for i in range(len(text) - N - 1):
            ngrams.add(hash(" ".join(text[i:i+N - 1])))
    ngrams = tuple(ngrams)
    for ng in index:
        if similarity(ng, ngrams) > THRESH:
            return True # TRUE IS BAD, SINCE IT MEANS ITS SIMILAR
    index.add(ngrams)
    return False # FALSE IS GOOD, IT MEANS THE PAGE IS NOT SIMILAR


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

SOFT404KEYWORDS = {"page","whoops","trouble","error","cannot","not","found","exist","404"}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link) and link not in unique_pages]

def extract_next_links(url, resp):
    global longest_page, word_counter, unique_pages
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

    if resp.status == 200 and resp.raw_response:
        # if not resp.raw_response:
        #     return links
        soup = BeautifulSoup(resp.raw_response.content, "lxml")

        #Tokenize, update longest page, unique pages, and word_counter

        #get rid of unwanted non-content tags
        for unwanted_tag_group in ["meta", "script", 'style', 'noscript']:
            for unwanted_tag in soup(unwanted_tag_group):
                unwanted_tag.clear()

        #get visible text, ignore 1 letter words    
        words = soup.getText(separator = " ", strip = True)#().split()

        """
        text_bytes = words.encode("utf-8", "ignore")
        page_hash = hashlib.sha1(text_bytes).digest()

        if page_hash in seen_hashes:
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                try:
                    finished_url = urljoin(url, href)
                except ValueError:
                    continue
                finished_url, _ = urldefrag(finished_url)
                links.add(finished_url)
            return links
        
        seen_hashes.add(page_hash)
        """

        #NOTE: technically only asking for most common words, so I don't think numbers are needed
        tokens = re.findall(r"\b[a-zA-Z]{2,}\b", words.lower())

        # NEAR / EXACT SIMILARITY
        if near_similar(tokens, threegrams):
            return links

        # Soft 404 check
        if soup.title:
            soft404kw_count = 0
            THRESHOLD = 3
            for w in soup.title.getText().split():
                if w.lower() in SOFT404KEYWORDS:
                    soft404kw_count += 1
                    if soft404kw_count >= THRESHOLD:
                        return links

        token_amt = 0
        cur_tokens = defaultdict(int)
        stopword_count = 0

        for t in tokens:
            t = t.lower()
            if t.lower() not in STOPWORDS:
                cur_tokens[t.lower()] += 1
                token_amt += 1
            else:
                stopword_count += 1

        # Filter out low into
        if (len(tokens) == 0 or len(tokens) < 10 or (stopword_count / len(tokens) > 0.55 or len(set(tokens)) / len(tokens) < 0.03)):
            return links

        # Update overall total tokens and unique pages AFTER we've confirmed stopword ratio is low enough
        for k,v in cur_tokens.items():
            word_counter[k] += v

        # Update unique pages

        #NOTE: Similar to href loop. changed to use urldefrag() because sometimes urls have multiple fragments
        url, _ = urldefrag(url)
        unique_pages.add(url)


        if longest_page[1] < token_amt: # Update longest page
            longest_page = (url, token_amt)

        for anchor in soup.find_all('a', href = True):
            href = anchor['href']            
            finished_url = ""
            try:
                finished_url = urljoin(url,href) #makes full urls from relative paths
            except ValueError:
                #print("ValueError at " + url)
                continue

            # De-fragment ("defragment the URLs, i.e. remove the fragment part.")
            finished_url, _ = urldefrag(finished_url)

            links.add(finished_url)
    return links

def is_valid(url) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    #TODO: crawler traps (discord thread in #resources), notable: calendar, inf traps, 
    #TODO: Crawl all pages with high textual information content, so maybe decide validity based on token amount of a page?
    #TODO: Detect and avoid sets of similar pages with no information
    #TODO: Detect and avoid dead URLs that return a 200 status but no data >>>D: Dead URL (also known as a soft 404) check
    #TODO: Detect and avoid crawling very large files, especially if they have low information value - i.e add more extensions ( i think, she mentioned that we had to add more extensions in lectures)

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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|mpg|ppsx|txt)$", parsed.path.lower()) # added mpg (video file), ppsx and txt: non html page
        
        #NOTE: counting domains like physICS.uci.edu as valid even though not technically valid, so had to make stricter format
        valid_domain = bool(re.match(r"^(?:[\w-]+\.)?(ics|cs|informatics|stat)\.uci\.edu$", parsed.netloc.lower())) # valid_domain = bool(re.match(r".*ics.uci.edu.*|"r".*cs.uci.edu.*|" r".*informatics.uci.edu.*|" r".*stat.uci.edu.*", parsed.netloc.lower()))

        #TODO: add more questionable urls/traps here
        #NOTE: doku.php - long download times for relatively low value, r.php is commonly used to redirect to other sites that may be outside specified domains
        questionable_url = (bool(re.match(r".*/events/.*|.*/events.*|.*/event/.*|.*/event.*", parsed.path.lower())) or # Calendar traps
                            ("doku.php" in parsed.path.lower()) or
                            ("~eppstein/pix" in parsed.path.lower()) or # Bunch of pictures
                            (("grape.ics.uci.edu" in parsed.netloc.lower()) and ("version=" in parsed.query.lower() or "from=" in parsed.query.lower() or "timeline" in parsed.path.lower())) or # On certain webpages, grape has 70+ marginally different past versions which are all separate webpages.
                            ("~eppstein/bibs/" in parsed.path.lower()) or
                            ("https://cdb.ics.uci.edu/supplement/randomSmiles100K" == url) or
                            #NOTE: the two lines below are causing it to crawl only 4 links
                            ("http://www.ics.uci.edu/~eppstein/pubs/pubs.ff" == url) or # 30k word html in text form
                            ("https://studentcouncil.ics.uci.edu/board" == url) or # Low information value + strangely formatted page which returns scripts as text
                            (("stat.uci.edu" in parsed.netloc.lower()) and ("covid19" in parsed.path.lower())) or
                            ("covid19.ics.uci.edu" in parsed.netloc.lower()) or
                            ("r.php" in parsed.path.lower() and ("http" in parsed.query.lower())) or #redirectors, would redirect outside domain
                            (".php" in parsed.path.lower() and ("http" in parsed.query.lower()))) #.php redirects

        if questionable_url:
            return False

        return valid_domain and wanted_file_ext

    except TypeError:
        print ("TypeError for ", parsed)
        raise

