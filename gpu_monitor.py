import subprocess
import time
import pandas as pd
from matplotlib import pyplot as plt

def gpu_sample(file_name):
    
    command = [
        'nvidia-smi',
        '--query-gpu=timestamp,name,memory.used,utilization.gpu,utilization.memory,temperature.gpu,power.draw,clocks.gr,clocks.sm,clocks.mem,clocks.video',
        '--format=csv',
        '-f',  file_name
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"nvidia-smi error: {result.stderr}")

def live_plot(interval, fig, axes, gpu_data):
    plt.ion()
    try: 
        df1 = gpu_data[[' utilization.gpu [%]', ' utilization.memory [%]']]
        df2 = gpu_data[[' temperature.gpu']]
        df3 = gpu_data[[' power.draw [W]']]
        df4 = gpu_data[[' clocks.current.graphics [MHz]', ' clocks.current.sm [MHz]', ' clocks.current.memory [MHz]', ' clocks.current.video [MHz]']]

        segmentation = [df1, df2, df3, df4]   
        titles = ['Utilization [%]', 'Temperature [C]', 'Power Draw [W]', 'Clock Frequencies [MHz]']
        
        for x in range(4):
            axes[x].clear()
            for col in segmentation[x].columns:
                axes[x].plot(gpu_data['time_elapsed'], segmentation[x][col], label=col)
            axes[x].set_title(titles[x])
            axes[x].yaxis.tick_right()
            axes[x].legend()
            if (len(gpu_data) > 100):
                axes[x].set_xlim(gpu_data['time_elapsed'].iloc[-1] - 100*interval, gpu_data['time_elapsed'].iloc[-1])
        
        fig.tight_layout()
        plt.style.use('ggplot')
        plt.pause(interval)

    except Exception as e:
        print(f"Error while plotting: {e}")


def main():

    data_titles = [' utilization.gpu [%]', ' utilization.memory [%]', ' power.draw [W]', ' clocks.current.graphics [MHz]', ' clocks.current.sm [MHz]', ' clocks.current.memory [MHz]', ' clocks.current.video [MHz]']

    interval = 1
    gpu_data = pd.DataFrame()

    file_name = f'./output_csv/monitor_output.csv'
    fig, axes = plt.subplots(4, 1, sharex=True)

    for ax in axes[:-1]:
        ax.set_xticklabels([])

    try:
        while True:
            gpu_sample(file_name)
            new_data = pd.read_csv(file_name)
            new_data['timestamp'] = pd.to_datetime(new_data['timestamp'])
            new_data['time_elapsed'] = ['0']
            
            for title in data_titles:
                new_data[title] = pd.to_numeric(new_data[title].str.extract(r'(\d+\.?\d*)')[0])

            gpu_data = pd.concat([gpu_data, new_data])
            ref = gpu_data['timestamp'].iloc[0]
            gpu_data['time_elapsed'] = (gpu_data['timestamp'] - ref) / pd.Timedelta(seconds=1)
            
            live_plot(interval, fig, axes, gpu_data)

    except KeyboardInterrupt:
        gpu_data.to_csv("./final_output.csv")
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()