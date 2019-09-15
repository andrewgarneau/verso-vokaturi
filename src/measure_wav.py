import sys
import scipy.io.wavfile
import os.path
import Vokaturi
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
# import json


PORT = 8080
# Handler = http.server.SimpleHTTPRequestHandler

# class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
#     def _set_headers(self):
#         self.send_response(200)
#         self.send_header('Content-type', 'application/json')
#         self.end_headers()

#     def do_GET(self):
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"Hello World")

#     def do_POST(self):
#         content_length = int(self.headers['Content-Length'])
#         post_data = self.rfile.read(content_length)
#         print ('post data from client:')
#         print (post_data)

#         response = {
#             'status':'SUCCESS',
#             'data':'server got your post data'
#         }
#         self._set_headers()
#         self.wfile.write(json.dumps(response))
from flask import Flask, request, jsonify
app = Flask(__name__)


sys.path.append("../api")
#print("Loading library...")
Vokaturi.load("../lib/open/macos/OpenVokaturi-3-3-mac64.dylib")

def getEmotionFromWav(filePath):

    emotionDict = dict()

    if not (os.path.exists(filePath)):
        return

    #reading sound file
    (sample_rate, samples) = scipy.io.wavfile.read(filePath)
    print("   sample rate %.3f Hz" % sample_rate)

    #print("Allocating Vokaturi sample array...")
    buffer_length = len(samples)
    #print("   %d samples, %d channels" % (buffer_length, samples.ndim))
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:
        c_buffer[:] = samples[:] / 32768.0  # mono
    else:
        c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0  # stereo

    #print("Creating VokaturiVoice...")
    voice = Vokaturi.Voice(sample_rate, buffer_length)

    #print("Filling VokaturiVoice with samples...")
    voice.fill(buffer_length, c_buffer)

    #print("Extracting emotions from VokaturiVoice...")
    quality = Vokaturi.Quality()
    emotionProbabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotionProbabilities)

    if quality.valid:
        print("Neutral: %.3f" % emotionProbabilities.neutrality)
        print("Happy: %.3f" % emotionProbabilities.happiness)
        print("Sad: %.3f" % emotionProbabilities.sadness)
        print("Angry: %.3f" % emotionProbabilities.anger)
        print("Fear: %.3f" % emotionProbabilities.fear)
        emotionDict["neutrality"] = float("{:.3f}".format(emotionProbabilities.neutrality))
        emotionDict["happiness"] = float("{:.3f}".format(emotionProbabilities.happiness))
        emotionDict["sadness"] = float("{:.3f}".format(emotionProbabilities.sadness))
        emotionDict["anger"] = float("{:.3f}".format(emotionProbabilities.anger))
        emotionDict["fear"] = float("{:.3f}".format(emotionProbabilities.fear))

    voice.destroy()
    return emotionDict


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/verso', methods=['POST']) #allow both GET and POST requests
def verso():
    req_data = request.get_json()
    print(req_data['filePath'])

    return (getEmotionFromWav(req_data['filePath']))

if __name__ == '__main__':
    app.run()
        

# httpd = HTTPServer(('localhost',PORT), SimpleHTTPRequestHandler)
# httpd.serve_forever()




#print("Analyzed by: %s" % Vokaturi.versionAndLicense())

