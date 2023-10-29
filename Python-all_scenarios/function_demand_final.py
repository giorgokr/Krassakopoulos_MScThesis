import matplotlib.pyplot as plt
import numpy as np

# plot: final total demand by all consumers from prosumers and from pros+DSO in each hour - round

def demand_final(day, cons_f_pros, cons_f_pros_dso, num_hours):
    hours = np.arange(num_hours)
    fig, ax = plt.subplots() #Created a fig and ax object using plt.subplots() to have more control over the plot.
    
    ax.step(hours, cons_f_pros, where='post', label='demand from pros')
    ax.step(hours, cons_f_pros_dso, where='post', label='demand from pros+DSO')
    
    ax.set_title('Final demand to prosumers/pros+DSO - Day {}'.format(day + 1))
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
    