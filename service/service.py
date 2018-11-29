import json
import os
import logging;

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

from flask import Flask, request, Response

# Url for sharepoint site we woant to work on
URL = os.environ.get('SP_URL')

USERNAME = os.environ.get('SP_USERNAME')
PASSWORD = os.environ.get('SP_PASSWORD')

# Key for entity attribute containing name of list we want to work on
LIST_NAME = os.environ.get('SP_LIST_NAME', 'ListName')
# Key for entity attribute containing name of list item
LIST_ITEM_NAME = os.environ.get('SP_LIST_ITEM_NAME', 'ListItemEntityTypeFullName')

logging.getLogger().setLevel(os.environ.get("LOG_LEVEL", logging.DEBUG))

APP = Flask(__name__)

if not URL or not USERNAME or not PASSWORD:
    logging.error("URL, USERNAME or PASSWORD not found.")
    exit(1)


@APP.route('/send-to-list', methods=['POST'])
def send_to_list():
    """
    Send list of entities to one or more sharepoint lists.
    Every entity must have:

    ListName property - which list it need to be sent

    ListItemEntityTypeFullName property - name of list item as it defined in Sharepoint
    one way to find it out is to call
    https://<name>.sharepoint.com/sites/<site name>/_api/lists/GetByTitle('<list name>')
    end find value of ListItemEntityTypeFullName property

    Keys property -list of entity keys which will be sent to SharePoint list

    Entity shall not have "status" attribute as it is used to storing result of operation
    If this attribute exist its value will be replaced!

    :return: list of processed entities where status attribute will be populated with result of operation
    """
    entities = request.get_json()

    def generate(entities: list):
        yield '['
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            keys_to_send = entity['Keys']

            ctx_auth = AuthenticationContext(URL)
            if ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
                try:
                    ctx = ClientContext(URL, ctx_auth)
                    list_object = ctx.web.lists.get_by_title(entity[LIST_NAME])

                    item_properties_metadata = {'__metadata': {'type': entity[LIST_ITEM_NAME]}}
                    values_to_send = {key: str(entity[key]) for key in keys_to_send}
                    item_properties = {**item_properties_metadata, **values_to_send}

                    list_object.add_item(item_properties)
                    ctx.execute_query()
                    entity['status'] = "OK: Sendt til {}".format(entity[LIST_NAME])
                except Exception as e:
                    logging.error(e)
                    entity['status'] = "ERROR: En feil oppstått: {}".format(e)
            else:
                error = ctx_auth.get_last_error()
                logging.error(error)
                entity['status'] = "ERROR: {}".format(error)

            yield json.dumps(entity)
        yield ']'

    return Response(generate(entities), mimetype='application/json')


@APP.route('/get-from-list/<list_name>', methods=['GET'])
def get_from_list(list_name):
    """
    Fetch list of entities from given sharepoint list
    :param list_name:
    :return:
    """
    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            yield json.dumps(entity.properties)
        yield ']'

    ctx_auth = AuthenticationContext(URL)
    if ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
        ctx = ClientContext(URL, ctx_auth)
        list_object = ctx.web.lists.get_by_title(list_name)
        items = list_object.get_items()
        ctx.load(items)
        ctx.execute_query()
        return Response(generate(items), mimetype='application/json')


@APP.route('/get-site-users', methods=['GET'])
def get_site_users():
    """
    Fetch SharepointUsers users
    :return:
    """
    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            yield json.dumps(entity.properties)
        yield ']'

    ctx_auth = AuthenticationContext(URL)
    if ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
        ctx = ClientContext(URL, ctx_auth)
        user_col = ctx.web.site_users
        ctx.load(user_col)
        ctx.execute_query()
    return Response(generate(user_col), mimetype='application/json')


if __name__ == '__main__':
    APP.run(debug=logging.getLogger().isEnabledFor(logging.DEBUG), threaded=True, host='0.0.0.0', port=5000)
