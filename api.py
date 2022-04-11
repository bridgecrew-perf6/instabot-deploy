import requests as requests
import urllib.request as url
import time
import os
import shutil
import sys
import json
import requests
import cgi


from instabot import Bot
from PIL import Image
from pathlib import Path
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


def do_something(text1):
   word = text1
   for f in Path('img/').glob('*.gitkeep'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
   for f in Path('resized/').glob('*.gitkeep'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

   # Enter number of posts (As I added the Image recognition for caption feature later, I'd suggest keeping the number of posts to 1 as only 1 pic will be recognised at a time for this program to limit the API Usage)
   number = 1
   #word = "cat"    # Enter your search word here
   success = "success"
   dimension = 1080
   token_id = "_ZGXmNxN05csQPqOtJyFRQybjrYJQZ6PaFQD_SIg9so"    # Unsplash Token ID

   r = requests.get('https://api.unsplash.com/search/collections?query=' +
                    word+'&page=1&per_page=30&client_id='+token_id)
   data = r.json()
   data.keys()
   data['total']
   data['total_pages']
   data['results']
   data['results'][0].keys()
   data['results'][0]['cover_photo']
   count = 0
   for img_data in data['results']:
        file_name = "img/" + "image"+str(count) + ".jpg"
        img_url = img_data['cover_photo']['urls']['raw']
        suffix = '&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=' + \
            str(dimension)+'&fit=max'
        print(img_url)
        img_url = img_url + suffix
        url.urlretrieve(img_url, file_name)
        count += 1

        # To resize the downloaded image/s to make them fit for Instagram
        path = "img/"
        resized_path = "resized/"
        dirs = os.listdir(path)
        final_size = 1080;

        def resize_aspect_fit():
            for item in dirs:
                if item == '.DS_Store':
                    continue
                if os.path.isfile(path+item):
                    im = Image.open(path+item)
                    f, e = os.path.splitext(resized_path+item)
                    size = im.size
                    ratio = float(final_size) / max(size)
                    new_image_size = tuple([int(x*ratio) for x in size])
                    im = im.resize(new_image_size, Image.ANTIALIAS)
                    new_im = Image.new("RGB", (final_size, final_size))
                    new_im.paste(
                        im, ((final_size-new_image_size[0])//2, (final_size-new_image_size[1])//2))
                    new_im.save(f + 'resized.jpg', 'JPEG', quality=100)
        resize_aspect_fit()
        if(count >= number):
            break
        src = 'resized/'
        trg = '.'
 
        files=os.listdir(src)

        for fname in files:
            shutil.copy2(os.path.join(src,fname), trg)
        print("step2")

        #Image Recognition API by Imagga to get hashtags 

        api_key = 'acc_bbd4275c9be957b' #Free version gives 1000 free requests. I might have used 15-20 by now.
        api_secret = '989dd12bb2f36e444a80b26fface211e'
        image_path = 'img/image0.jpg' #Only kept 1 image at-a-time kinda function to limit the API usage. 

        response = requests.post(
            'https://api.imagga.com/v2/tags',
            auth=(api_key, api_secret),
            files={'image': open(image_path, 'rb')})
        hashtag_array = response.json() #Imagga API gives a large array of potential keywords recognised from image via machine learning, so all of them may not be accurate. Let's take only first 5 hashtags for accuracy
        h1 = '#'+(hashtag_array['result']['tags'][0]['tag']['en'])
        h2 = '#'+(hashtag_array['result']['tags'][1]['tag']['en'])
        h3 = '#'+(hashtag_array['result']['tags'][2]['tag']['en'])
        h4 = '#'+(hashtag_array['result']['tags'][3]['tag']['en'])
        h5 = '#'+(hashtag_array['result']['tags'][4]['tag']['en'])

        shutil.rmtree("config") #To empty the "config" folder that gets created everytime we run Instabot (necessary)

        #InstaBot library Implementation (private Instagram API wrapper)
        bot = Bot()

        bot.login(username="insta.b0b",password="instabob.123")
        dir_image = "resized/"

        for image in os.listdir(dir_image):
            bot.upload_photo(image, caption="#"+ word + " " + h1 + " " + h2 + " " + h3 + " " + h4 + " " + h5)
        print("step3")
   return success

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/join', methods=['GET','POST'])
def my_form_post():
    text1 = request.form['text1']
    word = request.args.get('text1')
    combine = do_something(text1)
    result = {
        "output": combine
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

