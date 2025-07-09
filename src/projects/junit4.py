
def junit4_result_str_processing(test_result_stdout):
    total_test = (test_result_stdout.split("Tests run: ")[1].split(",")[0])
    total_failed_test = (test_result_stdout.split("Failures: ")[1].split("\n")[0])

    return total_test, total_failed_test, 0

if __name__ == '__main__':
    pass