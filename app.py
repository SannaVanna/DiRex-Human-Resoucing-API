from src import createApp, db

if __name__ == "__main__":
    app = createApp()
    app.run(port=4000, debug=True)
    