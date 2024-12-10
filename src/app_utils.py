import warnings
import pandas as pd

def suppress_plotly_warnings():
    warnings.filterwarnings('ignore', category=FutureWarning, 
                          message='The default of observed=False is deprecated')
    warnings.filterwarnings('ignore', category=FutureWarning, 
                          message='When grouping with a length-1 list-like')