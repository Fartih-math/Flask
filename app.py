from flask import Flask, render_template, request, send_from_directory
import os

application = Flask(__name__)

@application.route('/', methods=['GET', 'POST'])
def index():
    # Detects if image exists inside static or root folder to prevent crash
    image_in_static = os.path.exists(os.path.join(application.static_folder, '4k_Mountain_Peak.jpg'))
    
    if request.method == 'POST':
        namaDepan = request.form['namaDepan']
        namaBelakang = request.form['namaBelakang']
        nama = '%s %s' % (namaDepan, namaBelakang)
        
        p = nama
        c_encrypted = ''
        k = 3
        
        for i in range(len(p)):
            shifted_char = chr(ord(p[i]) + k)
            c_encrypted = c_encrypted + shifted_char
            
        return render_template('response.html', nama_asli=nama, nama_encrypt=c_encrypted, image_in_static=image_in_static)
        
    return render_template('form.html', image_in_static=image_in_static)

@application.route('/4k_Mountain_Peak.jpg')
def serve_root_image():
    return send_from_directory(os.getcwd(), '4k_Mountain_Peak.jpg')

if __name__ == '__main__':
    application.run(debug=True)
