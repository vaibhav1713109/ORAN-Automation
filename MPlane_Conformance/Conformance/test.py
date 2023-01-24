import xmltodict
xmlc = """<?xml version="1.0" ?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
	<active-alarm-list xmlns="urn:o-ran:fm:1.0">
		<active-alarms>
			<fault-id>18</fault-id>
			<fault-source>Module</fault-source>
			<affected-objects>
				<name>Sync Module</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Synchronization Error</fault-text>
			<event-time>2000-11-04T00:00:55Z</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>23</fault-id>
			<fault-source>Module</fault-source>
			<affected-objects>
				<name>Module</name>
			</affected-objects>
			<fault-severity>MAJOR</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>FPGA SW update failed</fault-text>
			<event-time>2000-11-04T00:19:40Z</event-time>
		</active-alarms>
	</active-alarm-list>
</data>
"""


dict_alarm = xmltodict.parse(str(xmlc))
alrm_name = list(dict_alarm['data']['active-alarm-list']['active-alarms'])
list_alrm = {}
fault_id = []
fault_text = []
for i in alrm_name:
    if "fault-id" in i.keys() and "fault-text" in i.keys():
        fault_id.append(i["fault-id"])
        fault_text.append(i["fault-text"])
list_alrm["fault-id"] = fault_id
list_alrm["fault-text"] = fault_text
if 'FPGA SW update failed' in list_alrm['fault-text']:
    print('yes')

print(list_alrm)

