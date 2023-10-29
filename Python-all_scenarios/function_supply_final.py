import matplotlib.pyplot as plt
import numpy as np

######Plot the price in euro DSO will pay to prosumers, for the energy they sold to cons, DSO and both together

def supply_final(day, sup_f_cons, sup_f_cons_dso, num_hours):
    hours = np.arange(num_hours)
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, sup_f_cons, where='post', label='supply to cons')
    ax.step(hours, sup_f_cons_dso, where='post', label='supply to cons+DSO')
    
    ax.set_title('Final supply to consumers/cons+DSO - Day {}'.format(day + 1))
    ax.set_xlabel('Hour/Round') 
    ax.set_ylabel('Supply (kWh)')
    ax.grid(True, which='both', linestyle='--') # to enable the gridlines on both major and minor ticks.
    ax.minorticks_on() #to display minor tick marks.
    ax.grid(True, which='minor', linestyle=':', linewidth='0.5', color='black') #to show the mesh grid for minor ticks.
    
    # Set the x-axis ticks to show every hour value
    ax.set_xticks(hours) #to set the x-axis ticks explicitly. By using ax.set_xticks(hours), every hour value 
                            #will be displayed on the horizontal axis.
    
    ax.legend()
    plt.show()
    