
from flask import Flask

app = Flask(__name__)

# シングルントン構造のカウンタークラス
class Counter:
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.count = 0
        return cls.instance

    def increment(self):
        if self.count < 100:
            self.count += 2
        return self.count

    def get(self):
        return self.count

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/healthz')
def healthz():
    import random
    global count

    count = Counter()

    count.increment()

    if random.randint(0, 100) < count.get():
        return f"Server Error {count.get()}", 500
    return f"OK {count.get()}", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

