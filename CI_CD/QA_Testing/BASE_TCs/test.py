import lxml.etree

tree = lxml.etree.parse('/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/BASE_TCs/test.xml')
root = tree.getroot()

d = {}
for node in root:
    key = node.tag
    if node.getchildren():
        for child in node:
            key += '_' + child.tag
            d.update({key: child.text})
    else:
        d.update({key: node.text})
# print(d)

for key, val in d.items():
    print(key,' : ',val)