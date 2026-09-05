"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from bson import json_util

from mongo_x_ray_log.log_items.slow_item import SlowItem
from tests.mocking import gen_mock_write_output

LOGS = [
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:41:05.344+02:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn26","msg":"Slow query","attr":{"type":"command","ns":"Restaurant.pizzas","appName":"mongosh 2.5.6","command":{"find":"pizzas","filter":{"size":{"$in":["small","medium","large"]}},"batchSize":1,"lsid":{"id":{"$uuid":"eef6660c-6ef9-4492-a285-fab357f0b335"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$readPreference":{"mode":"primaryPreferred"},"$db":"Restaurant"},"planSummary":"COLLSCAN","cursorid":4878020600984711450,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"queryHash":"904CC0B3","planCacheKey":"44190532","reslen":291,"locks":{"FeatureCompatibilityVersion":{"acquireCount":{"r":1}},"Global":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"local","provenance":"implicitDefault"},"storage":{},"remote":"127.0.0.1:51204","protocol":"op_msg","durationMillis":20}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:41:05.347+02:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn26","msg":"Slow query","attr":{"type":"command","ns":"Restaurant.pizzas","appName":"mongosh 2.5.6","command":{"getMore":4878020600984711450,"collection":"pizzas","batchSize":1,"lsid":{"id":{"$uuid":"eef6660c-6ef9-4492-a285-fab357f0b335"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$readPreference":{"mode":"primaryPreferred"},"$db":"Restaurant"},"originatingCommand":{"find":"pizzas","filter":{"size":{"$in":["small","medium","large"]}},"batchSize":1,"lsid":{"id":{"$uuid":"eef6660c-6ef9-4492-a285-fab357f0b335"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$readPreference":{"mode":"primaryPreferred"},"$db":"Restaurant"},"planSummary":"COLLSCAN","cursorid":4878020600984711450,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"reslen":292,"locks":{"FeatureCompatibilityVersion":{"acquireCount":{"r":1}},"Global":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"local","provenance":"implicitDefault"},"storage":{},"remote":"127.0.0.1:51204","protocol":"op_msg","durationMillis":10}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:41:05.343+02:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn35","msg":"Slow query","attr":{"type":"command","ns":"admin.$cmd","command":{"replSetUpdatePosition":1,"optimes":[{"durableOpTime":{"ts":{"$timestamp":{"t":1758836459,"i":2}},"t":6},"durableWallTime":{"$date":"2025-09-25T21:40:59.855Z"},"appliedOpTime":{"ts":{"$timestamp":{"t":1758836459,"i":2}},"t":6},"appliedWallTime":{"$date":"2025-09-25T21:40:59.855Z"},"memberId":0,"cfgver":90188},{"durableOpTime":{"ts":{"$timestamp":{"t":1758836465,"i":14}},"t":6},"durableWallTime":{"$date":"2025-09-25T21:41:05.313Z"},"appliedOpTime":{"ts":{"$timestamp":{"t":1758836465,"i":14}},"t":6},"appliedWallTime":{"$date":"2025-09-25T21:41:05.313Z"},"memberId":1,"cfgver":90188},{"durableOpTime":{"ts":{"$timestamp":{"t":1758836465,"i":12}},"t":6},"durableWallTime":{"$date":"2025-09-25T21:41:05.295Z"},"appliedOpTime":{"ts":{"$timestamp":{"t":1758836465,"i":13}},"t":6},"appliedWallTime":{"$date":"2025-09-25T21:41:05.305Z"},"memberId":2,"cfgver":90188}],"$replData":{"term":6,"lastOpCommitted":{"ts":{"$timestamp":{"t":1758836465,"i":14}},"t":6},"lastCommittedWall":{"$date":"2025-09-25T21:41:05.313Z"},"lastOpVisible":{"ts":{"$timestamp":{"t":1758836465,"i":14}},"t":6},"configVersion":90188,"configTerm":-1,"replicaSetId":{"$oid":"6784fe50cedf1b22edae209f"},"syncSourceIndex":0,"isPrimary":false},"maxTimeMSOpOnly":30000,"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"tKRu+IoxPKucZv5awKzBooqBZbE=","subType":"0"}},"keyId":7553643405352370178}},"$db":"admin"},"numYields":0,"reslen":410,"locks":{},"remote":"127.0.0.1:51366","protocol":"op_msg","durationMillis":50}}'
    ),
    json_util.loads(
        '{"t":{"$date":"2025-09-25T23:41:05.350+02:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn26","msg":"Slow query","attr":{"type":"command","ns":"Restaurant.pizzas","appName":"mongosh 2.5.6","command":{"getMore":4878020600984711450,"collection":"pizzas","batchSize":1,"lsid":{"id":{"$uuid":"eef6660c-6ef9-4492-a285-fab357f0b335"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$readPreference":{"mode":"primaryPreferred"},"$db":"Restaurant"},"originatingCommand":{"find":"pizzas","filter":{"size":{"$in":["small","medium","large"]}},"batchSize":1,"lsid":{"id":{"$uuid":"eef6660c-6ef9-4492-a285-fab357f0b335"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1758836465,"i":14}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$readPreference":{"mode":"primaryPreferred"},"$db":"Restaurant"},"planSummary":"COLLSCAN","cursorid":4878020600984711450,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"reslen":289,"locks":{"FeatureCompatibilityVersion":{"acquireCount":{"r":1}},"Global":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"local","provenance":"implicitDefault"},"storage":{},"remote":"127.0.0.1:51204","protocol":"op_msg","durationMillis":40}}'
    ),
]


def test_slow_item_streams_raw_lines_and_writes_top_n(tmp_path):
    item = SlowItem(output_folder=str(tmp_path), config={})
    for log in LOGS:
        item.analyze(log)
    item.finalize_analysis()

    records = item._load_records()
    raw = [r for r in records if "query_hash" not in r]
    aggregated = [r for r in records if "query_hash" in r]
    # All raw slow lines are streamed (including system namespaces)...
    assert len(raw) == 4
    # ... while only non-system namespaces are aggregated into the top-N
    assert len(aggregated) == 2
    assert item._cache == aggregated

    # Sorted by count descending
    assert aggregated[0]["query_hash"] == "7178B674"
    assert aggregated[0]["count"] == 2
    assert aggregated[0]["duration"] == 50
    assert aggregated[0]["ns"] == "Restaurant.pizzas"
    assert aggregated[1]["query_hash"] == "904CC0B3"
    assert aggregated[1]["count"] == 1


def test_slow_item_applies_slow_operations_rules(tmp_path):
    item = SlowItem(output_folder=str(tmp_path), config={})
    for log in LOGS:
        item.analyze(log)
    item.finalize_analysis()

    titles = [result["title"] for result in item._test_result]
    # Both Restaurant.pizzas entries have COLLSCAN plan summaries
    assert titles.count("Collection Scan Detected") == 2


def test_slow_item_mock_output(tmp_path):
    item = SlowItem(output_folder=str(tmp_path), config={})
    output, item._write_output = gen_mock_write_output(item)
    for log in LOGS:
        item.analyze(log)
    item.finalize_analysis()

    # 4 streamed raw lines + 2 aggregated records at finalize
    assert len(output) == 6
    assert output[0]["id"] == 51803
    assert output[0]["attr"]["ns"] == "Restaurant.pizzas"
    assert "query_hash" in output[4]
