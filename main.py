import todoist
import datetime
from wox import Wox, WoxAPI
import json
import os
from todoistClient import TodoistClient
import dateUtils


class TodoistInt(Wox):
    COMMAND_HELP = "/help"
    COMMAND_ADD = "/add"
    COMMAND_ADD_END = "/"
    COMMAND_LIST = "/list"
    COMMAND_LIST_SHORT_1 = "/l"

    ICONS_PATH = "icons"

    def query(self, query):
        results = []

        query = query.strip()

        if query.startswith(self.COMMAND_HELP):
            return results + self.help_command(query)

        client, partial_results = self.get_todoist_client()
        if client is None:
            return results + partial_results

        if query.startswith(self.COMMAND_ADD) and query.endswith(self.COMMAND_ADD_END):
            return results + self.add_command(query, client.api)

        if query.startswith(self.COMMAND_LIST) or query.startswith(
            self.COMMAND_LIST_SHORT_1
        ):
            return results + self.list_tasks_command(client)

        return results

    def list_tasks_command(self, client):
        results = []

        for item in client.get_overdue():
            self.append_new_task_item(item, client.time_zone, results, "overdue")
        for item in client.get_due(0):
            self.append_new_task_item(item, client.time_zone, results, "today")
        for item in client.get_due(+1):
            self.append_new_task_item(item, client.time_zone, results, "tomorrow")

        if not results:
            results.append(
                {
                    "Title": "No items to show",
                    "SubTitle": "",
                    "IcoPath": f"{self.ICONS_PATH}/ok.png",
                }
            )

        return results

    def get_todoist_client(self) -> (TodoistClient, []):
        results = []
        try:
            client = TodoistClient(self.get_todoist_api_key())
        except Exception as e:
            results.append(
                {
                    "Title": f"An error occured during initialization of TodoistClient",
                    "SubTitle": str(e),
                    "IcoPath": f"{self.ICONS_PATH}/error.png",
                }
            )
        return client, results

    def help_command(self, command_txt):
        results = []
        results.append(
            self.new_help_item(
                f"td {self.COMMAND_LIST} or td {self.COMMAND_LIST_SHORT_1} - list all task which are due today, tomorrow or overdue",
                f"td {self.COMMAND_LIST}",
            )
        )
        results.append(
            self.new_help_item(
                f"td {self.COMMAND_HELP} - displaying this help",
                f"td {self.COMMAND_HELP}",
            )
        )
        results.append(
            self.new_help_item(
                f"td {self.COMMAND_ADD} - add new task [with due date]",
                f"td {self.COMMAND_ADD} do shopping [due:tomorrow]{self.COMMAND_ADD_END}",
            )
        )
        return results

    def new_help_item(self, title, sub_title):
        return {
            "Title": title,
            "SubTitle": sub_title,
            "IcoPath": f"{self.ICONS_PATH}/app.png",
        }

    def add_command(self, query, api):
        query = query.replace(self.COMMAND_ADD, "", 1).replace(self.COMMAND_ADD_END, "")
        results = []

        if "due:" in query:
            desc, due_string = query.split("due:")
            api.items.add(desc, due={"string": due_string})
        else:
            desc = query
            due_string = ""
            api.items.add(desc)

        commit_result = api.commit()

        if (
            commit_result.get("error_tag") == "LIMITS_REACHED"
            or commit_result.get("http_code") == 429
        ):
            results.append(
                {
                    "Title": f"Todoist API limit exceeded :( Pls try again later...",
                    "SubTitle": str(commit_result),
                    "IcoPath": "Images/error.png",
                }
            )
        else:
            results.append(
                {
                    "Title": f"Item added. desc:{desc} due:{due_string}",
                    "SubTitle": str(commit_result),
                    "IcoPath": "Images/ok.png",
                }
            )

        return results

    def append_new_task_item(self, item, time_zone, results, icon):
        taskItem = self.create_task_item(item, icon, time_zone)
        results.append(taskItem)

    def create_task_item(self, item, category, time_zone):
        return {
            "Title": str(item["content"]) + " " + (item["priority"] - 1) * "*",
            "SubTitle": str(dateUtils.format_timestamp(item["due"]["date"], time_zone)),
            "IcoPath": f"{self.ICONS_PATH}/{category}.png",
            "ContextData": item["id"],
        }

    def mark_as_done(self, url):
        try:
            api = todoist.TodoistAPI(token=self.get_todoist_api_key())
            items = api.state["items"]
            filtered = [i for i in items if i["id"] == int(url)]
            item_to_complete = filtered[0]
            item_to_complete.complete()
            api.commit()
            api.sync()
            WoxAPI.show_msg("Marked as done", "GZ!")
        except Exception as e:
            WoxAPI.show_msg("Something went wrong :( :(", f"{str(e)}")

    def context_menu(self, data):
        results = []
        results.append(
            {
                "Title": "Mark as done",
                "SubTitle": "id: {}".format(str(data)),
                "IcoPath": f"{self.ICONS_PATH}/app.png",
                "JsonRPCAction": {
                    "method": "mark_as_done",
                    "parameters": [str(data)],
                    "dontHideAfterAction": False,
                },
            }
        )
        return results

    def get_todoist_api_key(self):
        config_file_name = "config.json"
        with open(
            os.path.join(os.path.dirname(__file__), config_file_name), "r"
        ) as config_file:
            config = json.loads(config_file.read())
        todoist_api_key = os.path.expandvars(config["todoist_api_key"])
        return todoist_api_key


if __name__ == "__main__":
    TodoistInt()
