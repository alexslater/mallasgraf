from flask import Flask
from forms import XLSForm

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return '<h1>Hello, World!</h1>'


@app.route('/reporter/<int:reporter_id>')
def reporter(reporter_id):
    return f'''
    <h2>Reporter {reporter_id} Bio</h2>
    <a href="/">Return to home page</a>
    '''

@app.route('/article/<article_name>')
def article(article_name):
  new_name = article_name.replace("-", " ").title()
  return f'''
  <h2>{new_name}</h2>
  <a href="/">Return back to home page</a>
  '''



if __name__ == '__main__':
    # El parámetro debug=True recarga automáticamente la app si hay cambios en el código
    app.run(debug=True)