from jeeves_cli.local_storage import storage

from jeeves_rest_client.client import JeevesClient


def with_client(func):
    def inject_client(*args, **kwargs):
        jeeves_master_host = storage.get_master_ip() or 'localhost'
        headers = {'Authorization':
                   'Bearer {}'.format(storage.get_access_token())}
        rest_client = JeevesClient(host=jeeves_master_host,
                                   headers=headers)
        return func(*args, client=rest_client, **kwargs)
    return inject_client
