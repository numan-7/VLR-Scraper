import scrapy
import requests
from spider.items import VlrItem

class UserPostsSpider(scrapy.Spider):
    name = 'vlr'
    allowed_domains = ['vlr.gg']
    base_url = 'https://vlr.gg'

    def __init__(self, username=None, *args, **kwargs):
        super(UserPostsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://vlr.gg/user/{username}']
        self.username = username
        self.processed_urls = set()
        self.user_item = VlrItem(
            upvotes=0, 
            downvotes=0, 
            upvote_count=0,
            downvote_count=0,
            dead_count=0,
            y0y_count=0,
            biggest_upvote=-1, 
            biggest_upvote_url='', 
            biggest_downvote=0, 
            biggest_downvote_url='', 
            biggest_upvote_quote ='', 
            biggest_downvote_quote = '',
            reply_user={}
        )

    def parse(self, response):
        # get total amount of pages of like posts a user has 
        page_links = response.css('a.btn.mod-page::attr(href)').getall()
        # errm get last page lol
        last_page_number = int(page_links[-1].split('=')[-1]) if page_links else 1
        # go through all the pages
        for page_number in range(1, last_page_number + 1):
            url = f'/user/{self.username}/?page={page_number}'
            yield response.follow(url, self.parse_user_page)
                
    def parse_user_page(self, response):
        # getting the link for all the posts on each page
        discussion_links = response.css('div.wf-card.ge-text-light a::attr(href)').getall()
        for link in discussion_links:
            # now um go to the page to get the comment link
            yield response.follow(link, self.parse_discussion)

    def parse_discussion(self, response):
        # check if the user is the original poster
        original_post_upvotes, original_post_downvotes = self.user_is_poster(response)
        # initialize or update the counts with the original post's counts
        if original_post_upvotes != -1 and original_post_downvotes != -1:
            self.user_item['upvotes'] += original_post_upvotes
            self.user_item['downvotes'] += original_post_downvotes
            if original_post_upvotes > 0 and original_post_downvotes == 0:
                self.user_item['upvote_count'] += 1
            elif original_post_downvotes < 0 and original_post_upvotes == 0:
                self.user_item['downvote_count'] += 1
            elif original_post_upvotes == 0 and original_post_downvotes == 0:
                self.user_item['dead_count'] += 1

        # find the user's comment(s) by the a tag
        user_posts = response.css(f'a.post-header-author[href*="/user/{self.username}"]')
        post_url_xpath = "./ancestor::div[contains(@class, 'wf-card post')]/div[contains(@class, 'post-footer')]/div[contains(@class, 'noselect')]/a[contains(@class, 'post-action link')]/@href"                
        # iterate through each comment and updating if necessary, this is self explantory
        for post_author in user_posts:
            post_url = self.get_full_url(post_author, post_url_xpath, response)
            # check if url is already processed
            if post_url in self.processed_urls: 
                continue
            # add 2 set :P
            self.processed_urls.add(post_url)
            upvote_count = post_author.xpath('./following-sibling::div[contains(@class,"post-frag-container")]/div[contains(@class,"positive")]/text()').get()
            downvote_count = post_author.xpath('./following-sibling::div[contains(@class,"post-frag-container")]/div[contains(@class,"negative")]/text()').get()
            neutral_count = post_author.xpath('./following-sibling::div[contains(@class,"post-frag-container")]/div[contains(@class,"neutral")]/text()').get()
            # yeah
            upvote_count = int(upvote_count) if upvote_count else 0
            downvote_count = int(downvote_count) if downvote_count else 0
            neutral_count = int(neutral_count) if neutral_count else -1

            reply_usernames = post_author.xpath('./ancestor::div[contains(@class, "threading")]/div[contains(@class, "threading")]/descendant::a[contains(@class, "post-header-author")]/text()')
            for username in reply_usernames:
                username = username.get().strip()
                if username and username != self.username:
                    if isinstance(self.user_item['reply_user'], dict):
                        if username in self.user_item['reply_user']:
                            self.user_item['reply_user'][username] += 1
                        else:
                            self.user_item['reply_user'][username] = 1
                    else:
                        self.user_item['reply_user'] = {username: 1}

            self.user_item['upvotes'] += upvote_count
            self.user_item['downvotes'] += downvote_count
            if upvote_count > 0 and downvote_count == 0:
                self.user_item['upvote_count'] += 1
            elif downvote_count < 0 and upvote_count == 0:
                self.user_item['downvote_count'] += 1
            elif neutral_count == 0 and upvote_count == 0 and downvote_count == 0:
                self.user_item['dead_count'] += 1

            # get full quote and then check for y0y in quote
            full_text_content = self.get_full_quote(post_author)
            if 'y0y' in full_text_content:
                self.user_item['y0y_count'] += 1

            if upvote_count > self.user_item['biggest_upvote'] or original_post_upvotes > self.user_item['biggest_upvote']:
                self.user_item['biggest_upvote'] = upvote_count if upvote_count > original_post_upvotes else original_post_upvotes
                self.user_item['biggest_upvote_url'] = self.get_full_url(post_author, post_url_xpath, response)
                self.user_item['biggest_upvote_quote'] = full_text_content
            if downvote_count < self.user_item['biggest_downvote'] or original_post_downvotes < self.user_item['biggest_downvote']:
                self.user_item['biggest_downvote'] = downvote_count if downvote_count < original_post_downvotes else original_post_downvotes
                self.user_item['biggest_downvote_url'] = self.get_full_url(post_author, post_url_xpath, response)
                self.user_item['biggest_downvote_quote'] = full_text_content

        yield self.user_item
        
        continue_links = response.css('a:contains("continue thread")::attr(href)').getall()
        for link in continue_links:
            yield response.follow(link, self.parse_discussion)

    def get_full_quote(self, post_author):
        # get content of the div that holds the users post
        post_body = post_author.xpath("./ancestor::div[contains(@class, 'wf-card post')]/div[contains(@class, 'post-body')]")
        # extract all text nodes
        text_nodes = post_body.xpath(".//text()").getall()
        # concate them
        full_text_content = " ".join(text_nodes).strip()
        return full_text_content
    
    def get_full_url(self, post_author, post_url_xpath, response):
        post_url = post_author.xpath(post_url_xpath).get()
        return response.urljoin(post_url)

    def user_is_poster(self, response):
        # extract the username of the original post author
        original_post_author = response.xpath('//a[@id="1"]/following-sibling::div[contains(@class, "post-header")]/a[contains(@class, "post-header-author")]/text()').get()
        if original_post_author and original_post_author.strip() == self.username:
            # the user is the original poster, proceed to get the count
            count = response.xpath('//div[@id="thread-frag-count"]/text()').get()
            count = int(count.strip()) if count else 0
            if count > 0:
                return count, 0
            elif count < 0:
                return 0, count
            return 0, 0
        else:
            # The user is not the original poster
            return -1, -1

    def closed(self, reason):
        requests.post('http://web:8000/update_scrapy_status', data={'task_id': self.username, 'is_completed': True})
