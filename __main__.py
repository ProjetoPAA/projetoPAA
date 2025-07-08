import src.py_app

if __name__ == '__main__':
    
    from nltk import download
    download('punkt')
    download('stopwords')
    download('rslp')
    src.py_app.app.run(debug=True)