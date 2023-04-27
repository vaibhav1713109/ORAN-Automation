alarm_name = [{'fault-id': '2', 'fault-source': 'Temp_2', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:38+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_3', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_4', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_5', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_6', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_7', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_8', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '2', 'fault-source': 'Temp_9', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Unit dangerously overheating', 'event-time': '2103-11-04T07:09:39+00:00'}, {'fault-id': '137', 'fault-source': 'Power_5', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'MAJOR', 'is-cleared': 'false', 'fault-text': 'Unit Power is high', 'event-time': '2103-11-04T07:09:41+00:00'}, {'fault-id': '137', 'fault-source': 'Power_6', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'MAJOR', 'is-cleared': 'false', 'fault-text': 'Unit Power is high', 'event-time': '2103-11-04T07:09:41+00:00'}, {'fault-id': '137', 'fault-source': 'Power_7', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'MAJOR', 'is-cleared': 'false', 'fault-text': 'Unit Power is high', 'event-time': '2103-11-04T07:09:41+00:00'}, {'fault-id': '137', 'fault-source': 'Module', 'affected-objects': {'name': 'Processor'}, 'fault-severity': 'MAJOR', 'is-cleared': 'false', 'fault-text': 'Unit Power is high', 'event-time': '2103-11-04T07:09:41+00:00'}, {'fault-id': '18', 'fault-source': 'Module', 'affected-objects': {'name': 'Sync Module'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'Synchronization Error', 'event-time': '2103-11-04T07:09:49+00:00'}, {'fault-id': '138', 'fault-source': 'Module', 'affected-objects': {'name': 'Module'}, 'fault-severity': 'CRITICAL', 'is-cleared': 'false', 'fault-text': 'DHCP and link failure', 'event-time': '2103-11-04T07:09:45+00:00'}]

xml_pretty_fm = '''<?xml version="1.0" ?>
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
	<active-alarm-list xmlns="urn:o-ran:fm:1.0">
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_2</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:38+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_3</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_4</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_5</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_6</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_7</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_8</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>2</fault-id>
			<fault-source>Temp_9</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit dangerously overheating</fault-text>
			<event-time>2103-11-04T07:09:39+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>137</fault-id>
			<fault-source>Power_5</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>MAJOR</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit Power is high</fault-text>
			<event-time>2103-11-04T07:09:41+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>137</fault-id>
			<fault-source>Power_6</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>MAJOR</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit Power is high</fault-text>
			<event-time>2103-11-04T07:09:41+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>137</fault-id>
			<fault-source>Power_7</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>MAJOR</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit Power is high</fault-text>
			<event-time>2103-11-04T07:09:41+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>137</fault-id>
			<fault-source>Module</fault-source>
			<affected-objects>
				<name>Processor</name>
			</affected-objects>
			<fault-severity>MAJOR</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Unit Power is high</fault-text>
			<event-time>2103-11-04T07:09:41+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>18</fault-id>
			<fault-source>Module</fault-source>
			<affected-objects>
				<name>Sync Module</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>Synchronization Error</fault-text>
			<event-time>2103-11-04T07:09:49+00:00</event-time>
		</active-alarms>
		<active-alarms>
			<fault-id>138</fault-id>
			<fault-source>Module</fault-source>
			<affected-objects>
				<name>Module</name>
			</affected-objects>
			<fault-severity>CRITICAL</fault-severity>
			<is-cleared>false</is-cleared>
			<fault-text>DHCP and link failure</fault-text>
			<event-time>2103-11-04T07:09:45+00:00</event-time>
		</active-alarms>
	</active-alarm-list>
</data>
'''
list_alrm = {}
fault_id = []
fault_text = []
# print(alarm_name)
for i in alarm_name:
    if "fault-id" in i.keys() and "fault-text" in i.keys():
        fault_id.append(i["fault-id"])
        fault_text.append(i["fault-text"])
if 'No external sync source' in fault_text:
    print(xml_pretty_fm)
else:
    print(fault_text)