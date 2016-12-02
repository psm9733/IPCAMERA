
def set_resolution(resolution):
    if resolution == "1920x1080":
            resolution = (1920,1080)
    elif resolution == "1280x720":
            resolution = (1280,720)
    else:
            resolution = (640,480)    
    return resolution
def get_width(resolution):
    if resolution == "1920x1080":
        return 1920
    elif resolution == "1280x720":
        return 1280
    else:
        return 640

def get_height(resolution):
    if resolution == "1920x1080":
        return 1080
    elif resolution == "1280x720":
        return 720
    else:
        return 480
