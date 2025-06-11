import requests
import pandas as pd
import numpy as np
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    # Create a sample DataFrame
    df = pd.DataFrame({
        'A': np.random.rand(5),
        'B': np.random.rand(5)
    })
    print(df)
    app.run(debug=True)