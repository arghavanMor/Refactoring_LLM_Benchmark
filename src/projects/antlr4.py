
def antlr4_result_str_processing(test_result_stdout):
    failed_test = None
    test_error = None

    test_result_summary_start = test_result_stdout.find("Results :")
    test_result_summary_end = test_result_stdout.rfind("Skipped")+12
    test_result_summary = test_result_stdout[test_result_summary_start:test_result_summary_end]

    if test_result_summary == '':
        failed_test, test_error = set(), set()
        return failed_test, test_error

    failed_test_temp = test_result_summary.split("Failed tests:")[1]
    failed_test = failed_test_temp.split("Tests in error:")[0]
    failed_test_list = [item.strip().split(")")[0]+")" for item in failed_test.split("\n") if 'test' in item]
    failed_test_list = [
        item.split(".")[1].split(":")[0] if item.startswith("Test") else item.split("(")[0]
        for item in failed_test_list
    ]
    failed_test = set(failed_test_list)

    if len(test_result_summary.split("Tests in error:")) == 2:
        test_error_temp = test_result_summary.split("Tests in error:")[1]
        test_error = test_error_temp.split("Tests run:")[0]
        test_error_list = [item.strip().split(")")[0]+")" for item in test_error.split("\n") if 'test' in item]
        test_error_list = [
            item.split(".")[1].split(":")[0] if item.startswith("Test") else item.split("(")[0]
            for item in test_error_list
        ]
        test_error = set(test_error_list)
        return failed_test, test_error
    else:
        return failed_test, set()


if __name__ == '__main__':
    pass