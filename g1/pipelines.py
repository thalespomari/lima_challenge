# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from google.cloud import bigquery
from google.oauth2 import service_account

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import signals


class G1Pipeline:
    bq_cliente = None

    def open_spider(self, spider):
        key_path = "/mnt/c/Users/lima-coding-challenge-2cf328969c17.json"

        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        self.bq_cliente = bigquery.Client(credentials=credentials, project=credentials.project_id)

    def save_to_bq(self, item):
        dataset_id = 'g1_scrapy'
        table_ref = self.bq_cliente.dataset(dataset_id).table('g1_news')
        table = self.bq_cliente.get_table(table_ref)

        ROWS_TO_INSERT = [
            (item['title'],
             item['link'],
             item['author'],
             item['subtitle'],
             item['datetime'])
        ]

        errors = self.bq_cliente.insert_rows(table, ROWS_TO_INSERT)
        print(errors)

    def process_item(self, item, spider):
        print(f"Pipeline: {item['author']}")
        self.save_to_bq(item)
        return item
