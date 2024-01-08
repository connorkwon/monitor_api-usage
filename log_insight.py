query_raw = """
fields requestTime, routeKey, status, clientId
| filter clientId = '{app_client['ClientId']}'
| filter (status = 200) or (status >= 400 and status < 500)
| filter routeKey != 'GET /'
| filter routeKey != 'GET /version'
| filter @timestamp >= 1702607410000 and @timestamp < {int(end_time.timestamp()) * 1000}
"""

# | filter @timestamp >= {int(start_time.timestamp()) * 1000} and @timestamp < {int(end_time.timestamp()) * 1000}

query_count = """
fields requestTime, routeKey, status, clientId
| filter clientId = '{app_client['ClientId']}'
| filter (status = 200) or (status >= 400 and status < 500)
| filter routeKey != 'GET /'
| filter routeKey != 'GET /version'
| filter @timestamp >= 1702607410000 and @timestamp < {int(end_time.timestamp()) * 1000}
| count()
"""