import configparser


# Writing Data
def WriteData(dic,filename):
    config = configparser.ConfigParser()
    config.read(filename)

    try:
        config.add_section("INFO")
    except configparser.DuplicateSectionError:
        pass
    for key,val in dic.items():
        config.set("INFO", key, val)
    with open(filename, "w") as config_file:
        config.write(config_file)
    print('Data append...')