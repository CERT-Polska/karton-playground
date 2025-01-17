from karton.core import Karton, Task, Resource
import subprocess


class StringsKarton(Karton):
    """
    Runs the `strings` utility on incoming samples
    """

    identity = "karton.strings"
    filters = [{"type": "sample", "stage": "recognized"}]

    def process(self, task: Task) -> None:
        # Get the incoming sample
        sample_resource = task.get_resource("sample")

        # Log with self.log
        self.log.info(f"Hi {sample_resource.name}, let me analyse you!")

        # Download the resource to a temporary file
        with sample_resource.download_temporary_file() as sample_file:
            # And run `strings` on it
            strings = subprocess.check_output(["strings", sample_file.name])

        # Send our results for further processing or reporting
        task = Task(
            {"type": "sample", "stage": "analyzed"},
            payload={"parent": sample_resource, "sample": Resource("string", strings)},
        )
        self.send_task(task)


if __name__ == "__main__":
    # Here comes the main
    StringsKarton.main()
