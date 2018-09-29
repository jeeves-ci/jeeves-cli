import json
import os

from jeeves_cli.constants import (CLI_LOCAL_DATA_FILE,
                                  CLI_WORKDIR)


class LocalStorage(object):

    def get_local_data(self):
        return self._load_local_data()

    @staticmethod
    def _load_local_data():
        if os.path.isfile(CLI_LOCAL_DATA_FILE):
            with open(CLI_LOCAL_DATA_FILE) as f:
                return json.load(f)
        return {}

    def get_logs(self, client_id, tail=False):
        pass

    def set_rabbitmq_ip(self, ip):
        self._set_key('rabbitmq_ip', ip)

    def set_postgres_ip(self, ip):
        self._set_key('redis_ip', ip)

    def set_master_ip(self, ip):
        self._set_key('master_ip', ip)

    def get_postgres_ip(self):
        return self.get_local_data().get('redis_ip')

    def get_rabbitmq_ip(self):
        return self.get_local_data().get('rabbitmq_ip')

    def get_master_ip(self):
        return self.get_local_data().get('master_ip')

    def get_access_token(self):
        return self.get_local_data().get('access_token')

    def set_access_token(self, token):
        self._set_key('access_token', token)

    def _set_key(self, key, val):
        local_data = self.get_local_data()
        local_data.update({key: val})
        with open(CLI_LOCAL_DATA_FILE, 'w') as f:
            json.dump(local_data, f)

    def init_local_storage(self):
        if not os.path.exists(CLI_WORKDIR):
            os.makedirs(CLI_WORKDIR)
        with open(CLI_LOCAL_DATA_FILE, 'w+') as f:
            f.write(json.dumps({}))


storage = LocalStorage()
