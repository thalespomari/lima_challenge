import scrapy

from g1.items import G1Item


class CrawlingSpiderG1(scrapy.Spider):
    name = "homepage"
    start_urls = ["https://g1.globo.com/"]

    custom_settings = {
        'FEEDS': {
            'g1_news.csv': {
                'format': 'csv',
                'overwrite': True
            }
        }
    }

    def parseNoticia(self, response, **kwargs):
        items = G1Item()

        # Not video allowed
        if not response.xpath("// div[@class='playlist__container']"):
            if response.xpath('// div[contains(@class, "top__signature") ]'):  # Blog
                author = response.xpath('// p[@class="top__signature__text__author-name"]/text()').get()
            else:
                author = response.xpath("// p[@class='content-publication-data__from']/text()").get()

            items['author'] = author.replace('Por ', '').replace(', g1', '').strip()
            items['title'] = kwargs['title']
            items['link'] = kwargs['link']
            items['subtitle'] = response.xpath("// h2[@class='content-head__subtitle']/text()").get()
            items['datetime'] = response.xpath("// p[@class ='content-publication-data__updated']/time/text()").get()
            yield items

    def parse(self, response, **kwargs):
        news_list = response.xpath('//div[@class="bastian-page"]/div[@class="_evg"]/div[@class="_evt"]')

        for news in news_list:
            title = news.css("a.feed-post-link::text").get()
            link = news.css("a.feed-post-link::Attr('href')").get()
            if link:
                yield response.follow(link,
                                      callback=self.parseNoticia,
                                      cb_kwargs={
                                          'title': title,
                                          'link': link
                                      })

        next_page = response.xpath('// div[contains(@class, "load-more")]/a/@href').get()
        if int(next_page.replace('.ghtml', '').split('-')[-1]) <= 10:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
