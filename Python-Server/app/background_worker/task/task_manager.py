import json
import pickle
import os
from collections import namedtuple

from background_worker.task.remove_task import RemoveTask
from background_worker.task.task import Task
from server_utils.utils import SETTINGS_FOLDER
import sys


class TaskManager:
    def __init__(self, logging, notion_ai):
        self.tasks_path = SETTINGS_FOLDER + 'tasks.json'
        self.logging = logging
        self.notion_ai = notion_ai
        self.tasks_json = []
        self.tasks = self._init_tasks()

    def _init_tasks(self):
        if os.path.isfile(self.tasks_path):
            print("Tasks json file found.")
            tasks = []
            with open(self.tasks_path, 'r') as json_file:
                self.tasks_json = json.load(json_file)

            for task in self.tasks_json:
                if task["type"] == "RemoveTask":
                    t = RemoveTask(dic=task, client=self.notion_ai.client)
                elif task["type"] == "Task":
                    t = Task(dic=task)

                tasks.append(t)

            return tasks
        else:
            print("No tasks assigned yet.")
            return []

    def find_task(self, task_to_find):
        for index, task in enumerate(self.tasks):
            if task.task_id == task_to_find.task_id:
                return index
        return -1

    def add_task(self, task):
        index = self.find_task(task)
        if index == -1:
            self.tasks_json.append(task.to_dic())
            self.tasks.append(task)
        else:
            self.tasks_json[index] = task.to_dic()
            self.tasks[index] = task

        self.save_tasks_to_json()

    def remove_task(self, task):
        self.tasks.remove(task)
        self.save_tasks_to_json()

    def save_tasks_to_json(self):
        if len(self.tasks) == 0:
            os.remove(self.tasks_path)
        else:
            with open(self.tasks_path, 'w') as outfile:
                json.dump(self.tasks_json, outfile)
