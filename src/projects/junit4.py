
def junit4_result_str_processing(test_result_stdout):
    test_result_summary_start = test_result_stdout.find("Results :\n")
    #test_result_summary_end = test_result_summary_start[test_result_summary_start]
    test_result_summary = test_result_stdout[test_result_summary_start:]

    total_test = test_result_summary[test_result_summary.find('run: ') + 5:test_result_summary.find(', Failures')]
    failed_test = test_result_summary[test_result_summary.find('Failures: ') + 10:test_result_summary.find(', Errors')]
    error_test = test_result_summary[test_result_summary.find('Errors: ') + 8:test_result_summary.find(', Skipped')]
    print(test_result_summary)
    total_test = int(total_test)
    total_failed_test = int(failed_test)
    total_error_test = int(error_test)
    return total_test, total_failed_test, total_error_test


if __name__ == '__main__':
    pass