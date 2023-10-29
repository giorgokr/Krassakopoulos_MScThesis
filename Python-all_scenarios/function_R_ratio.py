import matplotlib.pyplot as plt
import numpy as np

###### plot: R ratio Values for every hour

def R_ratio(day,  R_values, num_hours):
    
    # Plot the data
    hours = np.arange(num_hours) # Create an array of hours for the x-axis  
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, R_values, where='post')
    
    ax.set_title('ED/ES ratio - Day {}'.format(day + 1))
    ax.set_xlabel('Hour')
    ax.set_ylabel('R (ED/ES)')
    ax.grid(True, which='both', linestyle='--') # to enable the gridlines on both major and minor ticks.
    ax.minorticks_on() #to display minor tick marks.
    ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black') #to show the mesh grid for minor ticks.
    # Set the x-axis ticks to show every hour value
    ax.set_xticks(hours) #to set the x-axis ticks explicitly. By using ax.set_xticks(hours), every hour value 
    #will be displayed on the horizontal axis.
    plt.show()
    