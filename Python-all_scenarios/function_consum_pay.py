import matplotlib.pyplot as plt
import numpy as np

######Plot the price in euro consumers pay to prosumers, DSO and both together

def consum_pay(day, agent_b, pay_pros, pay_DSO, pay_both, num_hours):
    hours = np.arange(num_hours)
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, pay_pros, where='post', label='pay to pros')
    ax.step(hours, pay_DSO, where='post', label='pay to DSO ')
    ax.step(hours, pay_both, where='post', label='pay to pros+DSO')
    
    ax.set_title('Price comparison consumers pay to prosemers/DSO/both - Day {0} - Seller {1}'.format(day + 1, agent_b + 1)) 
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
    