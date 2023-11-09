import time, sys, re, requests
from bs4 import BeautifulSoup

base_url = 'https://vlr.gg'

# initialize a session object with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
})

# function to fetch the html content and return a soup object
def get_html_page(url):
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:  
            print("Invalid username or page not found.")
        else:
            print(f"HTTP error occurred: {http_err}") 
        sys.exit(1)
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit(1)
    return BeautifulSoup(response.text, 'lxml')

# function to process a discussion page for votes and continue thread links
def process_discussion_page(discussion_url, username, visited_urls, total_votes):
    print("Checking discussion: " + discussion_url)
    discussion_soup = get_html_page(discussion_url)

    # find all posts by the user in the discussion
    user_posts = discussion_soup.find_all('a', class_='post-header-author', href=f"/user/{username}")
    for post_author in user_posts:
        frag_container = post_author.find_next_sibling('div', class_='post-frag-container')
        if frag_container:
            upvote_div = frag_container.find('div', class_='post-frag-count positive')
            downvote_div = frag_container.find('div', class_='post-frag-count negative')
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

    # look for "continue thread" link and process it if it exists
    continue_link = discussion_soup.find('a', string=re.compile(r'continue thread'))
    if continue_link:
        continue_url = f"{base_url}{continue_link['href']}"
        if continue_url not in visited_urls:
            visited_urls.add(continue_url)
            process_discussion_page(continue_url, username, visited_urls, total_votes)

# start processing user votes
def get_user_votes(username):
    user_url = f'{base_url}/user/{username}'

    total_votes = {'upvotes': 0, 'downvotes': 0, 'biggest_upvote' : 0, 'biggest_upvote_url': ''}
    visited_urls = set()

    start_time = time.time()

    soup = get_html_page(user_url)
    page_links = soup.find_all('a', class_='btn mod-page')
    total_pages = int(page_links[-1].get_text(strip=True)) if page_links else 1

    for page_number in range(1, total_pages + 1):
        page_url = f"{user_url}/?page={page_number}"
        print(f"Checking page: {page_url}")
        soup = get_html_page(page_url)
        cur_page_discussions = soup.find_all('a', href=re.compile(r'^/\d+/[^/]+$'))
        
        for link in cur_page_discussions:
            discussion_url = f"{base_url}{link['href']}"
            if discussion_url not in visited_urls:
                visited_urls.add(discussion_url)
                process_discussion_page(discussion_url, username, visited_urls, total_votes)

    end_time = time.time()

    print(f"Total upvotes for {username}: {total_votes['upvotes']}")
    print(f"Total downvotes for {username}: {total_votes['downvotes']}")
    print(f"Net votes for {username}: {total_votes['upvotes'] + total_votes['downvotes']}")
    print(f"Biggest Upvote Count & Url: {total_votes['biggest_upvote']} {total_votes['biggest_upvote_url']}" )
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")


username = input("Enter username: ")
get_user_votes(username)