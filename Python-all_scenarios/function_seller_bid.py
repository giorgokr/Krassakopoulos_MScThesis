import matplotlib.pyplot as plt
import numpy as np

######Plot each sellers initial bids

def seller_bid(day, agent_s, seller_bid, num_hours):
    
    # Plot the data
    hours = np.arange(num_hours) # Create an array of hours for the x-axis
        
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, seller_bid, where='post') # creating a step-like appearance in the connection of seller_bid points
    
    ax.set_title('Seller Offer Bid Quantity - Day {0} - Seller {1}'.format(day + 1, agent_s + 1))
    ax.set_xlabel('Hour')
    ax.set_ylabel('Offer Quantity - Supply (kWh)')
    ax.grid(True, which='both', linestyle='--') # to enable the gridlines on both major and minor ticks.
    ax.minorticks_on() #to display minor tick marks.
    ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black') #to show the mesh grid for minor ticks.

    # Set the x-axis ticks to show every hour value
    ax.set_xticks(hours) #to set the x-axis ticks explicitly. By using ax.set_xticks(hours), every hour value 
                            #will be displayed on the horizontal axis.
    plt.show()
    
    