### This folder contains the evaluation data and the scripts used while evaluating the system performance of WUI Auto Evaluate.

- The evaluation data is compiled and can be seen easily in `metrics_calc.time_xlsx`.
- The shell script `evaluate_metrics_single_url.sh` is used to send metric evaluation requests to the server to evaluate the specified URL/
  - Example usage:
    - `evaluate_metrics_single_url.sh  metrics=m1,m2,m4,m10 requests=100 url="https://wui-eval.web.app"` will send 100 requests consecutively to the server to compute the metrics with IDs m1,m2,m4, and m10 for the URL https://wui-eval.web.app.
    - The output is a .txt file listing the time required to finish the request for each attempt.
- The python script `txt_to_csv.py` is used to convert the .txt files to csv format.
- The python script `generate_chart.py` is used to generate a box plot for the metric computation times
  