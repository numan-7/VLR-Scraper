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
        self.user_item = VlrItem(upvotes=0, downvotes=0, biggest_upvote=-1, biggest_upvote_url='', biggest_downvote=0, biggest_downvote_url='', biggest_upvote_quote ='', biggest_downvote_quote = '')

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

            upvote_count = int(upvote_count) if upvote_count else 0
            downvote_count = int(downvote_count) if downvote_count else 0

            self.user_item['upvotes'] += upvote_count
            self.user_item['downvotes'] += downvote_count

            text_content = "./ancestor::div[contains(@class, 'wf-card post')]/div[contains(@class, 'post-body')]/p"
            
            if upvote_count > self.user_item['biggest_upvote']:
                self.user_item['biggest_upvote'] = upvote_count
                self.user_item['biggest_upvote_url'] = self.get_full_url(post_author, post_url_xpath, response)
                self.user_item['biggest_upvote_quote'] = self.get_full_quote(post_author, text_content)
            if downvote_count < self.user_item['biggest_downvote']:
                self.user_item['biggest_downvote'] = downvote_count
                self.user_item['biggest_downvote_url'] = self.get_full_url(post_author, post_url_xpath, response)
                self.user_item['biggest_downvote_quote'] = self.get_full_quote(post_author, text_content)

        yield self.user_item
        
        continue_links = response.css('a:contains("continue thread")::attr(href)').getall()
        for link in continue_links:
            yield response.follow(link, self.parse_discussion)

    def get_full_quote(self, post_author, text_content):
        p_tags = post_author.xpath(text_content)
        # if top comment is in a spoiler div ^-^
        if not p_tags:
            text_content = "./ancestor::div[contains(@class, 'wf-card post')]/div[contains(@class, 'post-body')]//div[contains(@class, 'spoiler js-post-spoiler')]/p"
            p_tags = post_author.xpath(text_content)
        all_text_contents = []
        for p in p_tags:
            # pirect text 
            direct_text = p.xpath("text()").get()
            if direct_text:
                all_text_contents.append(direct_text)
            # text from <br> elements...please be only edge case im giong to kms
            br_texts = p.xpath("./br/following-sibling::text()").getall()
            all_text_contents.extend(br_texts)
            
        return " ".join(all_text_contents)
    
    def get_full_url(self, post_author, post_url_xpath, response):
        post_url = post_author.xpath(post_url_xpath).get()
        return response.urljoin(post_url)

    def closed(self, reason):
        requests.post('http://web:8000/update_scrapy_status', data={'task_id': self.username, 'is_completed': True})
