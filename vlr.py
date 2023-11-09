import time, sys, re, requests
import concurrent.futures
from bs4 import BeautifulSoup

base_url = 'https://vlr.gg'
# create a session with custom headers to simulate a web browser
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
})

# function to request and parse a webpage into a beautifulsoup object
def get_html_page(url):
    try:
        response = session.get(url)
        response.raise_for_status()  # check for http errors
    except requests.exceptions.HTTPError as http_err:
        # specific error handling for http errors
        if response.status_code == 404:
            print("Invalid username or page not found.")
        else:
            print(f"HTTP error occurred: {http_err}") 
        sys.exit(1)  # exit if there's an http error
    except Exception as err:
        # general error handling for other issues
        print(f"An error occurred: {err}")
        sys.exit(1)  # exit if any other error occurs
    return BeautifulSoup(response.text, 'lxml')  # return the parsed html page

# function to process individual discussion pages for a user's votes
def process_discussion_page(discussion_url, username, visited_urls, total_votes):
    print("Checking discussion: " + discussion_url)
    discussion_soup = get_html_page(discussion_url)

    # find posts by a specific user and tally the votes
    user_posts = discussion_soup.find_all('a', class_='post-header-author', href=f"/user/{username}")
    for post_author in user_posts:
        # find the voting elements and add to the total count
        frag_container = post_author.find_next_sibling('div', class_='post-frag-container')
        if frag_container:
            upvote_div = frag_container.find('div', class_='post-frag-count positive')
            downvote_div = frag_container.find('div', class_='post-frag-count negative')
            # update the total vote counts
            if upvote_div:
                parsedCount = int(upvote_div.get_text(strip=True))
                total_votes['upvotes'] += parsedCount
                if parsedCount > total_votes['biggest_upvote']:
                    total_votes['biggest_upvote'] = parsedCount
                    # Find the URL from the <a> tag with class 'post-action link' in a 'div' with class 'noselect'
                    biggest_upvote_link = post_author.find_next('div', class_='post-footer').find('div', class_='noselect').find('a', class_='post-action link')
                    if biggest_upvote_link:
                        total_votes['biggest_upvote_url'] = f"{base_url}{biggest_upvote_link['href']}"
            if downvote_div:
                total_votes['downvotes'] += int(downvote_div.get_text(strip=True))

    # find if there's a continuation of the thread and process it recursively
    continue_link = discussion_soup.find('a', string=re.compile(r'continue thread'))
    if continue_link:
        continue_url = f"{base_url}{continue_link['href']}"
        if continue_url not in visited_urls:
            visited_urls.add(continue_url)
            process_discussion_page(continue_url, username, visited_urls, total_votes)

# fetch discussion links from a user's page
def fetch_discussion_links(page_url):
    page_soup = get_html_page(page_url)
    # return all discussion links found on the page
    return page_soup.find_all('a', href=re.compile(r'^/\d+/[^/]+$'))

# the main function to get a user's total upvotes and downvotes
def get_user_votes(username):
    user_url = f'{base_url}/user/{username}'
    
    # initialize counts and visited urls set
    total_votes = {'upvotes': 0, 'downvotes': 0, 'biggest_upvote' : 0, 'biggest_upvote_url': ''}
    visited_urls = set()

    start_time = time.time()  # record the start time
    
    # get the first page to find out how many pages there are
    soup = get_html_page(user_url)
    page_links = soup.find_all('a', class_='btn mod-page')
    total_pages = int(page_links[-1].get_text(strip=True)) if page_links else 1
    
    # list to hold all discussion urls
    discussion_urls = []

    # use multithreading to fetch all discussion pages
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as page_executor:
        page_urls = [f"{user_url}/?page={i}" for i in range(1, total_pages + 1)]
        page_futures = [page_executor.submit(fetch_discussion_links, page_url) for page_url in page_urls]
        
        # as each page is fetched, extract the discussion urls
        for future in concurrent.futures.as_completed(page_futures):
            try:
                # get the list of discussion links from the future's result
                cur_page_discussions = future.result()
                for link in cur_page_discussions:
                    # build the complete URL for the discussion
                    discussion_url = f"{base_url}{link['href']}"
                    # if this URL has not already been visited
                    if discussion_url not in visited_urls:
                        # add it to the set of visited URLs to avoid duplication
                        visited_urls.add(discussion_url)
                        # add the discussion URL to the list for further processing
                        discussion_urls.append(discussion_url)
            except Exception as exc:
                print(f'Exception occurred: {exc}')

    # process each discussion page to count votes using multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as discussion_executor:
        discussion_futures = {discussion_executor.submit(process_discussion_page, url, username, visited_urls, total_votes): url for url in discussion_urls}
        # get the URL of the discussion page being processed
        for future in concurrent.futures.as_completed(discussion_futures):
            discussion_url = discussion_futures[future]
            try:
                # await the result of the future, which will be the completion of the vote counting for this discussion page
                future.result()  # the results update the total_votes
            except Exception as exc:
                print(f'Error processing {discussion_url}: {exc}')

    end_time = time.time()  # record the end time

    # print the results
    print(f"Total upvotes for {username}: {total_votes['upvotes']}")
    print(f"Total downvotes for {username}: {total_votes['downvotes']}")
    print(f"Net votes for {username}: {total_votes['upvotes'] + total_votes['downvotes']}")
    print(f"Biggest Upvote Count & Url: {total_votes['biggest_upvote']} {total_votes['biggest_upvote_url']}" )
    elapsed_time = end_time - start_time  # calculate elapsed time
    print(f"Time taken: {elapsed_time:.2f} seconds")

# start the script by asking for a username and calling the main function
username = input("Enter username: ")
get_user_votes(username)
