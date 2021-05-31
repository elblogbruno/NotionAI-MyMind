import schedule
import time
import threading


## coming soon
class Worker:
    def __init__(self, client, notion_ai):
        self.client = client
        self.notion_ai = notion_ai
        # self.background_job()
        # schedule.every().minute.do(self.background_job)

        # Start the background thread
        # stop_run_continuously = self.run_continuously()

        # Do some other things...
        # time.sleep(10)

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

    def background_job(self):
        print('Hello from the background thread')
        number_of_collections = self.notion_ai.mind_structure.get_number_of_collections()
        for i in range(0, number_of_collections):
            collection_id, id = self.notion_ai.mind_structure.get_collection_by_index(
                i)  # collection is our database or "mind" in notion, as be have multiple, if not suplied, it will get the first one as the priority one.
            collection = self.client.get_collection(collection_id=collection_id)

            cv = collection.parent.views[0]
            print(cv)
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
            print("Things assigned to me:", result)
