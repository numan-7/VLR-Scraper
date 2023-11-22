# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from djangospider.models import UserStats
from asgiref.sync import sync_to_async

class SpiderPipeline:
    async def process_item(self, item, spider):
        try:
            await sync_to_async(self.save_item)(item)
        except Exception as e:
            spider.logger.error(f"Error saving item: {e}")
        return item

    def save_item(self, item):
        # UserStats.objects.all().delete()
        post = UserStats(
            upvotes=item['upvotes'],
            downvotes=item['downvotes'],
            biggest_upvote=item['biggest_upvote'],
            biggest_upvote_url=item['biggest_upvote_url'],
            biggest_downvote=item['biggest_downvote'],
            biggest_downvote_url=item['biggest_downvote_url'],
            biggest_upvote_quote=item['biggest_upvote_quote'],
            biggest_downvote_quote=item['biggest_downvote_quote'],
        )
        post.save()
