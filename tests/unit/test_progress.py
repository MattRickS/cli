import mock

from cli import progress


@mock.patch("sys.stdout.write")
def test_progress(mock_write):
    cli_progress = progress.Progress()

    name = "Test"
    total = 100

    cli_progress.start_progress(total, name=name)
    output = mock_write.call_args[0][0]
    assert output == (
        "\rTest [                                                                 ]   0/100"
    )
    cli_progress.print_progress(50)
    output = mock_write.call_args[0][0]
    assert output == (
        "\rTest [================================                                 ]  50/100"
    )
    cli_progress.finish_progress()
    output, last = mock_write.call_args_list[-2:]
    assert last[0][0] == "\n"
    assert output[0][0] == (
        "\rTest [=================================================================] 100/100"
    )
