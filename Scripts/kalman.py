'''
Created on Nov 17, 2014

@author: Valentina
'''

class KalmanFilter:
    def __init__(self, initial_mean, initial_var):
        self.state_mean = float(initial_mean)
        self.state_var = float(initial_var)
        
    def update(self, mean, var):
        K = self.state_var / (self.state_var + var)
        new_mean = self.state_mean + K * (mean - self.state_mean)
        new_var = self.state_var - K * self.state_var
        self.state_mean = new_mean
        self.state_var = new_var
        return self.state()
    
    def state(self): 
        return self.state_mean, self.state_var