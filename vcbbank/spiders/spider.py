import datetime
import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import VcbbankItem
from itemloaders.processors import TakeFirst


class VcbbankSpider(scrapy.Spider):
	name = 'vcbbank'
	start_urls = ['https://www.vcb.bank/DesktopModules/EasyDNNNews/getnewsdata.ashx?language=en-US&portalid=0&tabid=85&moduleid=456&pageTitle=News+%7C+Virginia+Commonwealth+Bank&numberOfPostsperPage=999999&startingArticle=1']

	def parse(self, response):
		data = json.loads(response.text)['content']
		raw_data = scrapy.Selector(text=data)
		post_links = raw_data.xpath('//div[@class="article-title__text"]')
		for post in post_links:
			url = post.xpath('./h6/a/@href').get()
			day = post.xpath('.//span[@class="formatted"]/@day').get()
			month = post.xpath('.//span[@class="formatted"]/@month').get()
			year = post.xpath('.//span/@year').get()
			date = day+'.'+month+'.'+year
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

	def parse_post(self, response, date):
		title = response.xpath('//h4/text()').get()
		description = response.xpath('//div[@class="article-details__content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=VcbbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
