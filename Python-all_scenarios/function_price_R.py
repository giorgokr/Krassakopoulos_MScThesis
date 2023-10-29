import matplotlib.pyplot as plt
#import numpy as np

###### plot: R ratio Values for every hour

def price_R(day,  R_values, priceKWH):
    
    # Plot the data
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(R_values, priceKWH, where='post')
    #ax.plot(R_values, priceKWH)
    
    ax.set_title('common Price - ED/ES ratio for Day {}'.format(day + 1))
    ax.set_xlabel('R = ED/ES')
    ax.set_ylabel('Price (EUR/kWh)')
    ax.grid(True, which='both', linestyle='--') # to enable the gridlines on both major and minor ticks.
    ax.minorticks_on() #to display minor tick marks.
    ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black') #to show the mesh grid for minor ticks.
    # Set the x-axis ticks to show every hour value
    ax.set_xticks(R_values) #to set the x-axis ticks explicitly. By using ax.set_xticks(hours), every hour value 
                            #will be displayed on the horizontal axis.
    plt.show()
    