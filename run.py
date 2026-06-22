from app import create_app

app = create_app() # creates app

if __name__ == "__main__":
    app.run(debug=True) # starts web server