
import os
from pyccmetrics import Metrics
#Need tree-sitter==0.20.1


CODE_DIR = os.path.join(os.getcwd(), "src/java_files/test_single_line.java")


metrics = Metrics(file_path=CODE_DIR)
metrics.calculate()

print("Total CC: " + str(metrics.metrics_dict["VG_sum"]))
# print("Average CC: " + str(metrics.metrics_dict["VG_avg"]))
# print("Max CC: " + str(metrics.metrics_dict["VG_max"]))


print("Total method calls: " + str(metrics.metrics_dict["FOUT_sum"]))
# print("Average method calls: " + str(metrics.metrics_dict["FOUT_avg"]))
# print("Max method calls: " + str(metrics.metrics_dict["FOUT_max"]))

print("Total lines of code: " + str(metrics.metrics_dict["TLOC"]))
# print("Average lines of code: " + str(metrics.metrics_dict["MLOC_avg"]))
# print("Max lines of code: " + str(metrics.metrics_dict["MLOC_max"]))