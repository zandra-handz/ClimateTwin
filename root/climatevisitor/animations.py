# animation_updater.py

import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')  

def update_animation(latitude, longitude):
    pass

    plt.scatter(longitude, latitude)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Animation Update')
    plt.savefig('D:/CodingSpace/ClimateTwin/ClimateTwin/root/climatevisitor/animation.png')