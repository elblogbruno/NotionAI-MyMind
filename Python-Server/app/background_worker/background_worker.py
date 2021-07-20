import logging
from datetime import datetime
from urllib.error import HTTPError

import schedule
import time
import threading
import sys
import os
import tempfile

from background_worker.task.task_manager import TaskManager

dir_path = 'background_worker.log'
if getattr(sys, 'frozen', False):
    tmp = tempfile.mkdtemp()
    dir_path = os.path.join(tmp, 'notion-ai-app.log')

logging.basicConfig(filename=dir_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# # define a Handler which writes INFO messages or higher to the sys.stderr
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# # add the handler to the root logger
# logging.getLogger('').addHandler(console)
logging.info("Log file will be saved to temporary path: {0}".format(dir_path))

class Worker:
    def __init__(self, client, notion_ai):
        self.client = client
        self.notion_ai = notion_ai
        self.task_manager = TaskManager(logging, notion_ai)
        self.logging = logging
        # self.background_job()
        schedule.every(5).minutes.do(self.background_job)

        # Start the background thread
        self.stop_run_continuously = self.run_continuously()
        #
        # Do some other things...
        # time.sleep(10)
        #
        # Stop the background thread
        # stop_run_continuously.set()

    def run_continuously(self, interval=1):
        """Continuously run, while executing pending jobs at each
        elapsed time interval.
        @return cease_continuous_run: threading. Event which can
        be set to cease continuous run. Please note that it is
        *intended behavior that run_continuously() does not run
        missed jobs*. For example, if you've registered a job that
        should run every minute and you set a continuous run
        interval of one hour then your job won't be run 60 times
        at each interval but only once.
        """
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run

    def myFunc(self, e):
        return e.title == ""

    def _remove_blank_rows(self):
        number_of_collections = self.notion_ai.mind_structure.get_number_of_collections()
        for i in range(0, number_of_collections):
            collection_id, id = self.notion_ai.mind_structure.get_collection_by_index(
                i)  # collection is our database or "mind" in notion, as be have multiple, if not suplied, it will get the first one as the priority one.
            collection = self.client.get_collection(collection_id=collection_id)

            cv = collection.parent.views[0]
            self.logging.info("Analysing Collection #{0}".format(i))
            # Run a "filtered" query (inspect network tab in browser for examples, on queryCollection calls)
            filter_params = {
                "filters": [{
                    "filter": {
                        "operator": "is_empty"
                    },
                    "property": "title"
                }],
                "operator": "and"
            }
            result = cv.build_query(filter=filter_params).execute()

            self.logging.info("Analyzing this elements #{0}".format(result))

            self._remove_blank_blocks_from_list(result)

        self.logging.info("Background work remove blank rows finished at {0}".format(datetime.now()))

    def _remove_blank_blocks_from_list(self, list):
        for block in list:
            bl = self.client.get_block(block.id)
            title = bl.title
            url = bl.url
            multi_tag = self.notion_ai.property_manager.get_properties(bl, multi_tag_property=1)
            ai_tags = self.notion_ai.property_manager.get_properties(bl, ai_tags_property=1)
            mind_extension = self.notion_ai.property_manager.get_properties(bl, mind_extension_property=1)

            if len(title) == 0 and len(url) == 0 and len(multi_tag) == 0 and len(ai_tags) == 0 and len(
                    mind_extension) == 0:
                self.logging.info("Removing block with id: {0} as it is blank , title: {1}".format(bl.id, bl.title))
                self.logging.info("Have a look at this if you feel something bad was deleted")
                bl.remove()

    def _do_assigned_temporal_tasks(self):
        now = datetime.now()
        for task in self.task_manager.tasks:
            minutes_diff = (task.datetime_to_run - now).total_seconds() / 60.0
            if 1 < minutes_diff < 5:
                print("Doing temporal tasks at {0}".format(now))
                task.run_task()
                self.task_manager.remove_task(task)

    def background_job(self):
        if len(self.task_manager.tasks) > 0:
            self._do_assigned_temporal_tasks()

        time.sleep(2)

        try:
            self._remove_blank_rows()
        except HTTPError as e:
            logging.info(str(e))

