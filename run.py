from flask_app import create_app

app = create_app()

if __name__ == '__main__':
    print(f"Running app with database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True)
