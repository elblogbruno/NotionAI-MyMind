from datetime import datetime


class Task:

    def __init__(self, type="Task", task_id = None, datetime_to_run= None, dic= None):
        if dic:
            self._from_dic(dic)
        elif task_id and datetime_to_run and type:
            self.type = type
            self.task_id = task_id
            self.datetime_to_run = datetime_to_run
            self.task_dictionary = {}

    def _from_dic(self, dic):
        self.type = dic['type']
        self.task_id  = dic['task_id']
        self.datetime_to_run = datetime.strptime(dic['datetime_to_run'], "%Y-%m-%d %H:%M")

    def to_dic(self):
        dic = {
            "type": self.type,
            "task_id": self.task_id,
            "datetime_to_run": str(self.datetime_to_run)
        }
        self.task_dictionary = dic
        return self.task_dictionary

    def __str__(self):
        print("Task of type {0} at this time: {1}".format(self.type, self.datetime_to_run))

    def run_task(self):
        print("Running task of type {0} at this time: {1}".format(self.type, self.datetime_to_run))

