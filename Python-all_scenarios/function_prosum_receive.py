import matplotlib.pyplot as plt
import numpy as np

######Plot the price in euro DSO will pay to prosumers, for the energy they sold to cons, DSO and both together

def pros_rec(day, agent_s, rec_cons, rec_DSO, rec_both, num_hours):
    hours = np.arange(num_hours)
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, rec_cons, where='post', label='payment from cons')
    ax.step(hours, rec_DSO, where='post', label='payment from DSO')
    ax.step(hours, rec_both, where='post', label='payment from peers+DSO')
    #ax.plot(hours, buyer_bid)
    
    ax.set_title('Price comparison prosumers receive from consumers/DSO/both - Day {0} - Seller {1}'.format(day + 1, agent_s + 1)) 
    ax.set_xlabel('Hour/Round') 
    ax.set_ylabel('Price (EURO)')
    ax.grid(True, which='both', linestyle='--') # to enable the gridlines on both major and minor ticks.
    ax.minorticks_on() #to display minor tick marks.
    ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black') #to show the mesh grid for minor ticks.
    
    # Set the x-axis ticks to show every hour value
    ax.set_xticks(hours) #to set the x-axis ticks explicitly. By using ax.set_xticks(hours), every hour value 
                            #will be displayed on the horizontal axis.
    
    ax.legend()
    plt.show()
    