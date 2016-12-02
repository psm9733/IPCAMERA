def F_save(f_name, value, opt = None):
    if opt == None:
        Wfile = open("/home/pi/Desktop/project/info_"+f_name+".txt", 'w')
        Wfile.write(value)
        Wfile.close()
    elif opt == "a":
        Wfile = open("/home/pi/Desktop/project/info_"+f_name+".txt", 'a')
        Wfile.write(value)
        Wfile.close()
    
def F_read(f_name):
    Wfile = open("/home/pi/Desktop/project/info_"+f_name+".txt", 'r')
    value = Wfile.readline()
    Wfile.close()
    return value
