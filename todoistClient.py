import todoist
import datetime
from dateutil import tz
import dateUtils

class TodoistClient():
    def __init__(self, todoist_api_key):
        api = todoist.TodoistAPI(token=todoist_api_key)
        self._api = api

        self._api.sync()
        self._time_zone = tz.gettz(self._api.state['user']['tz_info']['timezone'])
        self._now = datetime.datetime.now(tz=self.time_zone)
 
    def sync(self):
        self._api.sync()

    def commit(self):
        self._api.commit()

    @property
    def state(self):
        return self._api.state

    @property
    def time_zone(self):
        return self._time_zone

    @property
    def items(self):
        return self._api.state['items']

    @property
    def api(self):
        return self._api

    def date_diff(self, timestamp): return dateUtils.format_timestamp(timestamp, self._time_zone).date() - self._now.date()

    def get_due_items (self):
        return filter(lambda x: x.data.get('due') != None and 'date' in x['due'] and x['due']['date'] != None and x['checked'] != 1, self.items)
    
    def get_due (self, days): return filter(lambda x: self.date_diff(x['due']['date']).days == days, self.get_due_items())

    def get_overdue (self): return filter(lambda x: self.date_diff(x['due']['date']).days < 0, self.get_due_items())
