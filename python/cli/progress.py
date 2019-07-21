import sys


class Progress(object):
    MAX_LENGTH = 80
    SYMBOL = "="

    def __init__(self, name_padding=None, number_padding=None):
        self.name = ""
        self.total = 0
        self._name_padding = name_padding
        self._number_padding = number_padding

    def start_progress(self, total, name=None):
        if total < 1:
            raise ValueError("Total must be greater than 0, got: {}".format(total))
        self.name = name or ""
        self.total = total
        self.print_progress(0)

    def print_progress(self, value):
        # Must use a minimum of 1 as formatting will fail with 0
        pad_name = max(1, self._name_padding or len(self.name))
        pad_num = self._number_padding or len(str(self.total))
        # pad_num is doubled for the number and total, 3 added for number
        # separator and spaces between name and bars
        pad_bar = self.MAX_LENGTH - (pad_name + pad_num * 2 + 3)
        sys.stdout.write(
            "\r{name:{pad_name}.{pad_name}} [{bars:{pad_bar}}] {progress:>{pad_num}}/{total}".format(
                name=self.name,
                bars=self.SYMBOL * int((value * pad_bar) / self.total),
                progress=value,
                total=self.total,
                pad_bar=pad_bar,
                pad_num=pad_num,
                pad_name=pad_name,
            )
        )

    def finish_progress(self, success=True):
        if success:
            self.print_progress(self.total)
        self.name = ""
        self.total = 0
        sys.stdout.write("\n")


def main():
    import time

    progress = Progress(number_padding=3)

    progress.start_progress(100, name="Some process")
    for i in range(100):
        time.sleep(0.05)
        progress.print_progress(i)
    progress.finish_progress()

    progress.start_progress(10, name="Some other process")
    for i in range(10):
        time.sleep(0.1)
        progress.print_progress(i)
    progress.finish_progress()

    progress.start_progress(10)
    for i in range(10):
        time.sleep(0.1)
        progress.print_progress(i)
    progress.finish_progress()


if __name__ == "__main__":
    main()
