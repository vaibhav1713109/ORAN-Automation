f = open('/usr/share/applications/splane.desktop',"w+")
l1 = "[Desktop Entry]\n"
l2 = "Name=Splane\n"
l3 = "Exec=python /home/vvdn/SPLANE_SUITE/parameters.py\n"
l4 = "Type=Application\n"
l5 = "Terminal=false\n"
l6 = "Comment=Helper to execute the S Plane Conformance test cases.\n"
l7 = "Icon=/home/vvdn/SPLANE_SUITE/icon.jpg\n"
f.writelines([l1 ,l2 ,l3 ,l4 ,l5 ,l6 ,l7])
f.close()