# -*- coding: utf-8 -*-
from urllib import parse

import datetime
import scrapy
import re
from scrapy.http import Request

from Article_spider.items import ArticleItem
from Article_spider.utils import common


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/page/300/']

    def parse(self, response):
        """
        获取文章列表中的文章url,并交给下载函数进行下载解析
        获取下一页的url,并进行下载，下载完成交给parse
        """
        post_urls = response.xpath('//a[@class="archive-title"]/@href').extract()
        image_urls = response.xpath('//*[@id="archive"]/div/div[1]/a/img/@src').extract()

        i = 0;
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_Detail,
                          meta={"front_img_url": parse.urljoin(response.url, image_urls[i])})
            i = i + 1

        # 提取下一页的url
        next_url = response.xpath("//a[contains(@class,'next page-numbers')]/@href").extract()[0]

        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_Detail(self, response):

        article = ArticleItem()
        front_image_url = response.meta.get("front_img_url", "")
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·","").strip()
        try:
            zan = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0])
        except Exception as e:
            zan=0
        collect = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]

        match_re = re.match(".*(\d+).*", collect)

        if match_re:
            collect = match_re.group(1)
        else:
            collect = 0

        comment = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]

        match_re = re.match(".*(\d+).*", comment)
        if match_re:
            comment = match_re.group(1)
        else:
            comment = 0

        content = response.xpath("//div[@class='entry']").extract()[0]

        tags = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()

        tags = [element for element in tags if not element.strip().endswith("评论")]

        tags = ",".join(tags)

        article["title"] = title
        try:
            create_time = datetime.datetime.strptime(create_time, "%Y/%m/%d").date()
        except Exception as e:
            create_time = datetime.datetime.now().date()
        article["create_time"] = create_time
        article["article_url"] = response.url
        article["article_url_obj"] = common.get_md5(response.url)
        article["front_img_path"] = front_image_url
        article["front_img_url"] = [front_image_url]
        article["zan"] = zan
        article["comment"] = comment
        article["collect"] = collect
        article["tags"] = tags
        article["content"] = content

        yield article
