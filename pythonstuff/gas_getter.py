import http.client
import json

def gas_getter():
    connection = http.client.HTTPSConnection("api.etherscan.io")
    connection.request("GET", "/api?module=gastracker&action=gasoracle&apikey=ZXQSEN5SHXSRIBTV2NQA2PDS7H6NMXXYH4")
    response = connection.getresponse()

    raw_data = response.read()
    encoding = response.info().get_content_charset('utf8')  # JSON default
    data = json.loads(raw_data.decode(encoding))
    return data