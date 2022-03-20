from broker import app
import os

if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV")
    if isinstance(env, str) and "main" in env.lower():
        app.run()
    else:
        app.run(debug=True)
