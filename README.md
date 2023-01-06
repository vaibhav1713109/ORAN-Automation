# ORAN-Automation
The repository is been build for  M &amp; S Plane optimisation in the Fronthual Interface

## Used Libraries: 
- Python >=3.7
- ncclient >=0.6.12
- fpdf2>=2.5.5
- lxml==4.8.0
- ifcfg>=0.22
- pytest>=7.0.1
- requests>=2.27.1
- tabulate>=0.8.10
- xmltodict>=0.13.0
- pyqt5>=5.15.6
- scapy>=2.5.0
- httplib2>=0.21.0

## Installation
- python -m pip install --upgrade pip
- pip install -r requirements.txt


## Setup Diagram

![M_Plane_Automation](https://user-images.githubusercontent.com/69416241/210972509-63f75236-dd1a-44b6-9209-418d64572fc5.png)

## Flow Chart
![S_Plane_Flow_chart](https://user-images.githubusercontent.com/69416241/210972318-9e5eca90-16b6-41f7-9a38-e4ccac5e1a4b.png)

## Usage
- File Structure of Root Directory

![file_structure](https://user-images.githubusercontent.com/69416241/210973779-9e650025-561d-4d45-b765-2fbe6553e0ef.png)
- File Structure of MPlane Conformance

![M_Plane_File_Structure](https://user-images.githubusercontent.com/69416241/210973871-3fa31167-7c37-4bfa-831b-ee7fcd212053.png)

- ** Run with GUI **
  - Go to the GUI directory.
  - Run below command
    -sudo python login.py
- ** Run with terminal **
  - Go to Conformance directory
  - Run below command
    - python config.py 
      - Note:  fill all the credentials which will be asked.
    - sudo python M_CTC_ID_{Test_Case_ID}.py
  - Note: run first config.py file before running the test cases so that all the latest data will be updated in inputs.ini file 



