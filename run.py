from app import create_app

 #create flask app
app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
