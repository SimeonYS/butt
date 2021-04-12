import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbuttItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.ky.butterfieldgroup.com/News/Pages/default.aspx?Year={}'

class BbuttSpider(scrapy.Spider):
	name = 'butt'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [base.format(year)]

	def parse(self, response):
		articles = response.xpath('//tr[@class="default"]')
		for article in articles:
			date = article.xpath('.//td[@class="default bottomBorderdot padL7"]/text()').get()
			post_links = article.xpath('.//td[@class="news_title bottomBorderdot"]//div[contains(@id,"collapse_expand-")]/div[@class="item link-item bullet"]/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		if self.year > 2008:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)


	def parse_post(self, response, date):
		title = response.xpath(
			'//h1/text() | //td[@class="news_title_detail"]/text() |//strong[@style="color: #660033"]/text()|//div[@class="ms-rteFontSize-2"]//div/strong/text()').get()
		content = response.xpath(
			'//div[@class="ms-WPBody ms-wpContentDivSpace"]/table/tbody/tr/td[last()]//text()[not (ancestor::h1 or ancestor::span[@id="HTMLHeader"] or ancestor::span[@id="subHeadText"])]|//div[@webpartid="cb811f84-064a-40f1-b7c5-f7a1fdf2ad1e"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "", ' '.join(content))

		item = ItemLoader(item=BbuttItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
