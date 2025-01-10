from cobochat import app, db

def resetDB():
    db.drop_all()
    app.app_context().push()
    db.create_all()

    print("Database Reset!")

resetDB()