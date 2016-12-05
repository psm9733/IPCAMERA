from flask import Flask, send_file, render_template, request, Response, make_response
import picamera
from camera_module import set_resolution, get_width, get_height
from f_module import F_save, F_read
import signal, os, time, io
from threading import Lock
import time
from time import sleep
import numpy as np
import random
import os,subprocess
from subprocess import Popen,PIPE
import json



app = Flask(__name__)
mode = 0
effect = 0
lck = Lock()
threshold =40
prior_image = None
bright = 0

def detect_motion(camera):
    print "detect_motion"
    global prior_image
    stream = io.BytesIO()
    camera.capture(stream, format='rgba', use_video_port=True)
    stream.seek(0)
    if prior_image is None:
        prior_image = np.fromstring(stream.getvalue(), dtype=np.uint8)
        return False
    else :
        current_image = np.fromstring(stream.getvalue(), dtype=np.uint8)
        #Compare current_image to prior_image to detect motion. This is
        #left as an exercise for the reader!
        #Once motion detection is done, make the prior image the current
        comp_image=np.abs(prior_image - current_image)
        numTrigger = np.count_nonzero(comp_image>threshold)/4
        prior_image=current_image
        lck.acquire()
        print(numTrigger)
        width = get_width(resolution)
        height = get_height(resolution)
        minPixelsChanged= width*height*50/100
        print(minPixelsChanged)
        lck.release()
        
        if numTrigger >minPixelsChanged:
            return True
        else :
            return False
        
        
def gen():
        while True:
                frame = get_frame()
                if frame == None:
                        break
                else:
                        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
def get_frame():
        global resolution, annotate, mode, effect
        with picamera.PiCamera() as camera:
                mode = int(mode)
                if mode != 1:
                        return None
                lck.acquire()
                camera.annotate_text = annotate
                camera.resolution = set_resolution(resolution)
                camera.brightness = bright
                if effect == 0:
                    camera.image_effect = 'none'
                elif effect == 1:
                    camera.image_effect = 'blur'
                elif effect == 2:
                    camera.image_effect = 'emboss'
                elif effect == 3:
                    camera.image_effect = 'cartoon'
                elif effect == 4:
                    camera.image_effect = 'denoise'
                elif effect == 5:
                    camera.image_effect = 'negative'
                print "resolution"
                print resolution
                lck.release()
                stream = io.BytesIO()
                camera.capture(stream, 'jpeg', use_video_port=True)
                stream.seek(0)
                return stream.read()
@app.route('/')
def index():
        fexist = os.path.exists("/home/pi/Desktop/project/info_Filename.txt")
        if not fexist: 
            wfile = open("/home/pi/Desktop/project/info_Filename.txt", 'w')
            wfile.close
        wfile = open("/home/pi/Desktop/project/info_Filename.txt", 'r')  
        wfile = wfile.read()
        lines = wfile.split("\n")
        return render_template('config.html', wjson = json.dumps(lines))

@app.route('/send_video' ,methods=['GET'])
def send_video():
        global filepath
        
        #filenames = request.form['multiple']
        filenames = request.args.get('multiple','')
        
        filenames = str(filenames)
        #ret_data = {"value": filenames}
        filepath = "/home/pi/Desktop/project/storage/"+filenames
        print filenames
        print filepath
        print os.path.exists(filepath)
        
        #return send_file(filepath, mimetype = "video/mp4")
        return "Ok"
     
@app.route('/get_video' ,methods=['GET'])
def get_video():
    return send_file(filepath, mimetype = "video/mp4")
    
@app.route('/config')
def config():
        global annotate, resolution, mode, effect
        annotate = request.args.get('annotate', '')
        mode = request.args.get('mode', '')
        effect = request.args.get('effect', '')
        resolution = request.args.get('resolution', '')
        bright = request.args.get('bright','')
        print annotate, mode, resolution, effect
        
        F_save("annotate", annotate)
        F_save("mode", mode)
        F_save("effect", effect)
        F_save("resolution", resolution)
        F_save("bright", bright)
        pid=F_read("pid")
        os.kill(int(pid), signal.SIGUSR1)
        return 'OK'

@app.route('/capture')
def capture():
        global mode, effect,bright
        mode = int(F_read("mode"))
        effect = int(F_read("effect"))
        bright = int(F_read("bright"))
        if mode == 0:
            try:       
                print "capture camera"
                camera = picamera.PiCamera()
                lck.acquire()
                camera.annotate_text = annotate
                camera.resolution = set_resolution(resolution)
                camera.brightness = bright
                if effect == 0:
                    camera.image_effect = 'none'
                elif effect == 1:
                    camera.image_effect = 'blur'
                elif effect == 2:
                    camera.image_effect = 'emboss'
                elif effect == 3:
                    camera.image_effect = 'cartoon'
                elif effect == 4:
                    camera.image_effect = 'donoise'
                elif effect == 5:
                    camera.image_effect = 'negative'
                camera.capture('/home/pi/Desktop/project/new_image.jpg')
                lck.release()
                camera.close()
            finally:
                camera.close()
            return send_file('/home/pi/Desktop/project/new_image.jpg')
        elif mode == 1:
                return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
                    try:   
                        lck.acquire()
                        camera = picamera.PiCamera()
                        camera.resolution = set_resolution(resolution)
                        stream=picamera.PiCameraCircularIO(camera,seconds=10)
                        camera.start_recording(stream, format='h264')
                        lck.release()
                        while True:
                            mode = int(F_read("mode"))
                            camera.wait_recording(1)
                            if detect_motion(camera):
                                    print('*****Motion detected!*****')
                                    filepath = "/home/pi/Desktop/project/storage/"
                                    camera.split_recording(time.strftime(filepath + "%Y%m%d%H%M%S")+'after.h264')
                                    filename = time.strftime("%Y%m%d%H%M%S")
                                    stream.copy_to(filepath + filename + 'before.h264', seconds=10)
                                    lck.acquire()
                                    F_save("Filename", filename +"after.mp4" , "a")
                                    lck.release()
                                    
                                    #cmd = ["MP4Box","-fps","30","-add",filepath + filename+"before.h264",filepath + filename+"before.mp4"]
                                    #popen = subprocess.Popen(cmd)
                                    stream.clear()
                                    camera.wait_recording(5)
        
                                    print('Motion stopped!')
                                    cmd = ["MP4Box","-fps","30","-add",filepath + filename+"after.h264",filepath + filename+"after.mp4"]
                                    popen = subprocess.Popen(cmd)
                                    # json filemake 
                                    #rfile = open("/home/pi/Desktop/project/info_Filename.txt", 'r')
                                    #wfile = open("/home/pi/Desktop/project/info_JSON.txt",'w')
                                    
                                    #roof_number = 0
                                    #wfile.write("[\n")
                                    #while True:
                                        #lines = rfile.readline()
                                        #if not lines:
                                            #break
                                        #line_t = lines.split("\n",1)
                                        #line_num = 0
                                        #for line in line_t:               
                                            #if not line:
                                                #if(roof_number > 1):
                                                    #wfile.write("}")
                                                    #break
                                                #break
                                                
                                            #if (roof_number == 0):
                                                #wfile.write("{\n")
                                                #wfile.write("\"display\": " + "\"" + line + "\",\n")
                                                #wfile.write("\"url\": " + "\"" + "/home/pi/Desktop/project/storage/" + line + "\"\n")
                                                #wfile.write("}")
                                                #roof_number = roof_number + 1
                                                
                                            #else:
                                                #wfile.write(",\n{\n")
                                                #wfile.write("\"display\": " + "\"" + line + "\",\n")
                                                #wfile.write("\"url\": " + "\"" + "/home/pi/Desktop/project/storage/" + line + "\"\n")
                                                #roof_number = roof_number + 1
                                    #wfile.write("}\n")
                                    #wfile.write("]\n")
                                    #wfile.close()
                                    #rfile.close()
                                    F_save("Filename", "\n" , "a")
                                    camera.split_recording(stream)
                            if mode != 2:
                                camera.stop_recording()
                                camera.close()
                                break
                            
                    finally:
                            print "error detection mode"
                            camera.close()
                            
if __name__ == '__main__':
        app.run(host='0.0.0.0', port = 5005, threaded=True)
