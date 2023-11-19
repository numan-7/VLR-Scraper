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
        self.user_item = VlrItem(upvotes=0, downvotes=0, biggest_upvote=0, biggest_upvote_url='')

    def parse(self, response):
        page_links = response.css('a.btn.mod-page::attr(href)').getall()
        last_page_number = int(page_links[-1].split('=')[-1]) if page_links else 1

        for page_number in range(1, last_page_number + 1):
            url = f'/user/{self.username}/?page={page_number}'
            yield response.follow(url, self.parse_user_page)
                
    def parse_user_page(self, response):
        discussion_links = response.css('div.wf-card.ge-text-light a::attr(href)').getall()
        for link in discussion_links:
            yield response.follow(link, self.parse_discussion)

    def parse_discussion(self, response):
        user_posts = response.css(f'a.post-header-author[href*="/user/{self.username}"]')
        for post_author in user_posts:
            upvote_count = post_author.xpath('./following-sibling::div[contains(@class,"post-frag-container")]/div[contains(@class,"positive")]/text()').get()
            downvote_count = post_author.xpath('./following-sibling::div[contains(@class,"post-frag-container")]/div[contains(@class,"negative")]/text()').get()

            upvote_count = int(upvote_count) if upvote_count else 0
            downvote_count = int(downvote_count) if downvote_count else 0

            self.user_item['upvotes'] += upvote_count
            self.user_item['downvotes'] += downvote_count

            if upvote_count > self.user_item['biggest_upvote']:
                self.user_item['biggest_upvote'] = upvote_count
                post_url_xpath = "./ancestor::div[contains(@class, 'wf-card post')]/div[contains(@class, 'post-footer')]/div[contains(@class, 'noselect')]/a[contains(@class, 'post-action link')]/@href"                
                post_url = post_author.xpath(post_url_xpath).get()
                self.user_item['biggest_upvote_url'] = response.urljoin(post_url)
        
        yield self.user_item
        
        continue_links = response.css('a:contains("continue thread")::attr(href)').getall()
        for link in continue_links:
            yield response.follow(link, self.parse_discussion)

    def closed(self, reason):
        requests.post('http://127.0.0.1:8000/update_scrapy_status', data={'task_id': self.username, 'is_completed': True})
