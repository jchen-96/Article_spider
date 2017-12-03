# -*- coding: utf-8 -*-
import json

import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
import codecs
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi


class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImage(ImagesPipeline):

    def item_completed(self, results, item, info):
        for ok, value in results:
            file_path = value["path"]
        item["front_img_path"] = file_path

        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.writelines(lines)
        return item

    def spider_close(self, spider):
        self.file.close()


class JsonExpoterPipeline(object):

    # 调用scrapy提供的json expoter 导出json文件
    def __init__(self):
        self.file = open("articleexport.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("127.0.0.1", "root", "2014080102", "article_spider", charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title,create_time,article_url,article_url_obj,front_img_url,front_img_path,zan,comment,collect,tags)
            VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (
            item["title"], item["create_time"], item["article_url"], item["article_url_obj"], item["front_img_url"],
            item["front_img_path"], item["zan"], item["comment"], item["collect"], item["tags"]))
        self.conn.commit()


class MysqlPool(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dpparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True

        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dpparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                   insert into article(title,create_time,article_url,article_url_obj,front_img_url,front_img_path,zan,comment,collect,tags)
                   VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               """
        cursor.execute(insert_sql, (
            item["title"], item["create_time"], item["article_url"], item["article_url_obj"], item["front_img_url"],
            item["front_img_path"], item["zan"], item["comment"], item["collect"], item["tags"]))
