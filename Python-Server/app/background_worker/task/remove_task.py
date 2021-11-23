from datetime import datetime

from background_worker.task.task import Task


class RemoveTask(Task):
    def __init__(self, block_id_to_remove= None, datetime_to_run= None, client= None, dic = None):
        if client:
            self.notion_client = client
        if dic:
            super().__init__(type="RemoveTask", dic = dic)
        elif block_id_to_remove and datetime_to_run:
            super().__init__(type="RemoveTask", task_id=block_id_to_remove, datetime_to_run=datetime_to_run)
            self.block_id_to_remove = block_id_to_remove


    def __str__(self):
        print("Task of type {0} at this time: {1}".format(self.type, self.datetime_to_run))

    def run_task(self):
        print("Removing block with id {0}".format(self.block_id_to_remove))
        block = self.notion_client.get_block(self.block_id_to_remove)
        block.remove()
        print("Block removed succesfully!")

    def _from_dic(self, dic):
        self.type = dic['type']
        self.task_id  = dic['task_id']
        self.datetime_to_run = datetime.strptime(dic['datetime_to_run'], "%Y-%m-%d %H:%M:%S")
        self.block_id_to_remove = dic['block_id_to_remove']

    def to_dic(self):
        dic = {
            "type": self.type,
            "task_id": self.task_id,
            "block_id_to_remove": self.block_id_to_remove,
            "datetime_to_run": str(self.datetime_to_run)
        }
        self.task_dictionary = dic
        return self.task_dictionary
