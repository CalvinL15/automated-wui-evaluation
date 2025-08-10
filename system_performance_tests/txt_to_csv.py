import csv

input_file = 'the name of the file that you want to convert to csv'
output_file = 'output.csv'

times = []
with open(input_file, 'r') as file:
    for line in file:
        time_str = line.split(': ')[1].strip(' s\n')
        times.append(float(time_str))

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    for time in times:
        formatted_time = f"{time:.2f}".replace('.', ',')
        writer.writerow([formatted_time])
