from scrapy import Request, Spider

from discusshk.items import CategoryItemLoader, TopicItemLoader, ThreadItemLoader, PostItemLoader, UserItemLoader


class HKDiscussSpider(Spider):
    name = 'hkdiscuss'
    start_urls = [
        'http://www.discuss.com.hk/forumdisplay.php?fid=190'
    ]

    crawlera_enabled = True
    default_headers = {'X-Crawlera-Cookies': 'disable'}

    def start_requests(self):
        for _ in self.start_urls:
            yield Request(_, headers={'X-Crawlera-Cookies': 'disable'})

    def parse(self, response):
        category = CategoryItemLoader(response=response)
        category.add_xpath('name', '//div[@class="topbar_gid"]/a/text()')
        category.add_xpath('id', '//div[@class="topbar_gid"]/a/@href', re=r'gid=(\d+)')
        category = category.load_item()
        topic = TopicItemLoader(response=response)
        topic.add_xpath('name', '//div[@class="topbar_fid1a"]/a/text()')
        topic.add_xpath('id', '//div[@class="topbar_fid1a"]/a/@href', re=r'fid=(\d+)')
        topic.add_value('category', category)
        topic = topic.load_item()
        metadata = {
            'topic': topic
        }
        discussions = response.xpath('//span[contains(@id, "thread")]/a/@href').extract()
        for discussion in discussions:
            yield Request(response.urljoin(discussion), self.parse_thread, meta={'metadata': metadata, 'page': 1},
                          headers=self.default_headers)
        next_page = response.xpath('//div[@class="pages"]/a[@class="next"]/@href').extract_first()
        if next_page:
            yield Request(response.urljoin(next_page), headers=self.default_headers)

    def parse_thread(self, response):
        page = response.meta.get('page', 1)
        metadata = response.meta.get('metadata', {})
        thread = ThreadItemLoader(response=response)
        thread.add_value('id', response.url, re=r'tid=(\d+)')
        thread.add_xpath('name', '//h1/text()')
        thread.add_value('topic', metadata.get('topic'))
        thread = thread.load_item()
        posts_sel = response.xpath('//table[contains(@id, "table-")]')
        for p in posts_sel:
            user = UserItemLoader(selector=p)
            user.add_xpath('id', './/div[contains(@id, "userinfo")]/@id', re=r'(\d+)')
            user.add_xpath('username', './/div[contains(@id, "userinfo")]/following-sibling::a/text()')
            user.add_xpath('n_posts', './/dt[text()="帖子"]/following-sibling::dd[1]/text()')
            user.add_xpath('integrity', './/dt[text()="積分"]/following-sibling::dd[1]/text()')
            user = user.load_item()
            post = PostItemLoader(selector=p)
            post.add_value('thread', thread)
            post.add_value('user', user)
            post.add_xpath('id', '@summary')
            post.add_value('page', page)
            post.add_xpath('body',
                           """
                           .//span[contains(@id, "postorig_")]/*[not(@class="quote")]//text() |
                           .//span[contains(@id, "postorig_")]/text()
                           """)
            post.add_xpath('timestamp', './/div[@class="postinfo"]/text()', re=r'(\d{4}\-\d+\-\d+ \d+\:\d+ .M)')
            post.add_xpath('quotes', './/blockquote/a/@href', re=r'pid=(\d+)')
            yield post.load_item()
        next_page = response.xpath('//a[@class="next" and text()="››"]/@href').extract_first()
        yield Request(response.urljoin(next_page), self.parse_thread, meta={'metadata': response.meta.get('metadata'),
                                                                            'page': page + 1},
                      headers=self.default_headers)

