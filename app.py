from src import createApp, db

if __name__ == "__main__":
    app = createApp()
    app.run(host='0.0.0.0', port=4000)
    